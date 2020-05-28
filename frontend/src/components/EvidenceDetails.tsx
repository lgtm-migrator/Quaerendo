import * as React from 'react'
import { Evidence } from '../openapi-types'
import { useGet } from 'restful-react'
import {
  Card,
  CardContent, ExpansionPanel,
  ExpansionPanelDetails,
  ExpansionPanelSummary,
  Grid,
  Theme,
  Typography
} from '@material-ui/core'
import AuthorsLinksList from './AuthorsLinksList'
import { makeStyles } from '@material-ui/styles'
import OpenInNewRoundedIcon from '@material-ui/icons/OpenInNewRounded'
import ExpandMoreIcon from '@material-ui/icons/ExpandMore'
import SourceInfo from './SourceInfo'

interface EvidenceDetailProps {
  id: number
}

const useStyles = makeStyles((theme: Theme) => ({
  card: {
    margin: theme.spacing(2)
  },
  description: {
    marginTop: theme.spacing(1)
  },
  link: {
    color: theme.palette.primary.main,
    textDecoration: 'none',
    '&:hover': {
      color: theme.palette.primary.light,
      textDecoration: 'underline'
    }
  },
  margin: {
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(2)
  },
  expansionPanel: {
    marginLeft: theme.spacing(2),
    marginRight: theme.spacing(2),
    marginBottom: theme.spacing(2)
  }
}))

const EvidenceDetails: React.FC<EvidenceDetailProps> = (props) => {
  const classes = useStyles()
  const [showSource, setShowSource] = React.useState(true)
  const [showReviews, setShowReviews] = React.useState(false)
  const {data} = useGet({
    path: '/api/evidence/' + props.id
  })
  let evidence: Evidence = undefined
  if (data) {
    evidence = data
  }
  return (
    <>
      <Card className={classes.card}>
        <CardContent>
          {
            evidence ?
              <>
                <Typography variant='h4' gutterBottom>
                  {
                    evidence.source_of_evidence.title !== '' ?
                      evidence.source_of_evidence.title
                      :
                      'Untitled Evidence'
                  }
                </Typography>
                <Typography variant='body1' component='p' className={classes.description}>
                  {
                    evidence.description !== '' ?
                      evidence.description
                      :
                      'No description has been provided for this piece of evidence.'
                  }
                </Typography>
              </>
              :
              ''
          }
        </CardContent>
      </Card>
      <div className={classes.expansionPanel}>
        <ExpansionPanel expanded={showSource} onChange={() => setShowSource(!showSource)}>
          <ExpansionPanelSummary
            expandIcon={<ExpandMoreIcon />}
          >
            <Typography variant='h5'>Source</Typography>
          </ExpansionPanelSummary>
          <ExpansionPanelDetails>
            {
              evidence ?
                <SourceInfo source={evidence.source_of_evidence} />
                :
                ''
            }
          </ExpansionPanelDetails>
        </ExpansionPanel>
      </div>
      <div className={classes.expansionPanel}>
        <ExpansionPanel expanded={showReviews} onChange={() => setShowReviews(!showReviews)}>
          <ExpansionPanelSummary
            expandIcon={<ExpandMoreIcon />}
          >
            <Typography variant='h5'>Reviews</Typography>
          </ExpansionPanelSummary>
          <ExpansionPanelDetails>
            <Typography variant='body1' paragraph>
              {
                evidence ?
                  evidence.num_expert_reviews === 0 ?
                    'This evidence has not been reviewed by experts.'
                    :
                    'This evidence has been reviewed by ' + evidence.num_expert_reviews + ' experts.'
                  :
                  ''
              }
            </Typography>
          </ExpansionPanelDetails>
        </ExpansionPanel>
      </div>
    </>
  )
}

export default EvidenceDetails
