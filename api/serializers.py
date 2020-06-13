import math

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from api.models import Entity, Source, Claim, Evidence, EvidenceReview, Topic, EvidenceRelationship


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ['id', 'name', 'short_bio']


class SourceSerializer(serializers.ModelSerializer):
    authors = EntitySerializer(many=True)

    class Meta:
        model = Source
        fields = '__all__'


class SourceCreateSerializer(serializers.ModelSerializer):
    authors = PrimaryKeyRelatedField(many=True, write_only=True, queryset=Entity.objects.all())

    class Meta:
        model = Source
        fields = '__all__'


class SourceLinkSerializer(serializers.ModelSerializer):
    authors = EntitySerializer(many=True, read_only=True)

    class Meta:
        model = Source
        fields = ['id', 'authors']


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['name']


class ClaimSerializer(serializers.ModelSerializer):
    topic = TopicSerializer(read_only=True)
    source_of_claim = SourceSerializer(read_only=True)

    class Meta:
        model = Claim
        fields = ['id', 'claim_text', 'description', 'topic', 'source_of_claim']


class ClaimCreateSerializer(serializers.ModelSerializer):
    topic = Topic.objects.first()
    source_of_claim = SourceCreateSerializer()

    class Meta:
        model = Claim
        fields = ['id', 'claim_text', 'description', 'topic', 'source_of_claim']

    def create(self, validated_data):
        source_data = validated_data.pop('source_of_claim')
        authors = source_data.pop('authors')
        source_instance = Source.objects.create(**source_data)
        source_instance.authors.set(authors)
        user = self.context['request'].user
        # TODO: Remove this Topic.objects.first()
        claim_instance = Claim.objects.create(**validated_data, source_of_claim=source_instance,
                                              topic=Topic.objects.first(), submitted_by=user)
        return claim_instance


class EvidenceSerializer(serializers.ModelSerializer):
    source_of_evidence = SourceSerializer(read_only=True)
    expert_consensus_relationship = serializers.SerializerMethodField()
    community_consensus_relationship = serializers.SerializerMethodField()
    num_expert_reviews = serializers.SerializerMethodField()
    num_community_reviews = serializers.SerializerMethodField()

    class Meta:
        model = Evidence
        fields = ['id', 'source_of_evidence', 'description', 'expert_consensus_relationship', 'num_expert_reviews',
                  'community_consensus_relationship', 'num_community_reviews']

    @staticmethod
    def get_consensus(obj: Evidence, expert: bool) -> EvidenceRelationship:
        topic_experts = obj.claim.topic.experts.all()
        if expert:
            reviews = obj.reviews.filter(reviewer__in=topic_experts)
        else:
            reviews = obj.reviews.exclude(reviewer__in=topic_experts)

        # If 80% of reviewers agree on an evidence relationship, return that. Otherwise, return 'SPLIT'.
        deduced_relationships_by_count = dict()
        num_expert_reviews = len(reviews)
        num_required_for_80_pct_consensus = math.ceil(num_expert_reviews * 0.8)
        for review in reviews:
            if review.deduced_evidence_relationship not in deduced_relationships_by_count:
                deduced_relationships_by_count[review.deduced_evidence_relationship] = 1
            else:
                deduced_relationships_by_count[review.deduced_evidence_relationship] += 1
        for relationship, count in deduced_relationships_by_count.items():
            if count >= num_required_for_80_pct_consensus:
                return relationship
        return EvidenceRelationship.SPLIT

    @extend_schema_field(serializers.ChoiceField(choices=EvidenceRelationship.choices))
    def get_expert_consensus_relationship(self, obj: Evidence) -> EvidenceRelationship:
        return self.get_consensus(obj, expert=True)

    @extend_schema_field(serializers.ChoiceField(choices=EvidenceRelationship.choices))
    def get_community_consensus_relationship(self, obj: Evidence) -> EvidenceRelationship:
        return self.get_consensus(obj, expert=False)

    @staticmethod
    def get_num_reviews(obj: Evidence, expert: bool) -> int:
        topic_experts = obj.claim.topic.experts.all()
        if expert:
            reviews = obj.reviews.filter(reviewer__in=topic_experts)
        else:
            reviews = obj.reviews.exclude(reviewer__in=topic_experts)
        return reviews.count()

    def get_num_expert_reviews(self, obj: Evidence) -> int:
        return self.get_num_reviews(obj, expert=True)

    def get_num_community_reviews(self, obj: Evidence) -> int:
        return self.get_num_reviews(obj, expert=False)


class EvidenceReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenceReview
        fields = ['deduced_evidence_relationship', 'deduced_source_degree', 'is_reliable',
                  'additional_comments']


class EvidenceWithReviewSerializer(serializers.ModelSerializer):
    source_of_evidence = SourceSerializer()
    reviews = EvidenceReviewSerializer(many=True)
    claim = serializers.PrimaryKeyRelatedField(queryset=Claim.objects.all())

    class Meta:
        model = Evidence
        fields = ['source_of_evidence', 'reviews', 'claim']

    def create(self, validated_data):
        source_data = validated_data.pop('source_of_evidence')
        authors = source_data.pop('authors')
        source_instance = Source.objects.create(**source_data)
        source_instance.authors.set(authors)
        review = EvidenceReviewSerializer(data=validated_data.pop('reviews'), many=True)
        claim = validated_data.pop('claim')
        user = self.context['request'].user
        evidence_instance = Evidence.objects.create(**validated_data, source_of_evidence=source_instance, claim=claim,
                                                    submitted_by=user)
        if review.is_valid():
            review_instance = review.save(evidence=evidence_instance, reviewer=user)
            evidence_instance.reviews.set(review_instance)
            evidence_instance.save()
        return evidence_instance


class EvidenceReviewPartialSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenceReview
        fields = ['deduced_evidence_relationship', 'additional_comments']


class ClaimWithEvidenceSerializer(serializers.ModelSerializer):
    topic = TopicSerializer(read_only=True)
    source_of_claim = SourceSerializer(read_only=True)
    related_evidence = EvidenceSerializer(many=True, read_only=True)

    class Meta:
        model = Claim
        fields = ['id', 'claim_text', 'description', 'topic', 'source_of_claim', 'related_evidence']
