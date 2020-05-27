import { createMuiTheme } from '@material-ui/core'

const MainTheme = createMuiTheme({
  palette: {
    primary: {
      main: '#800d0d'
    }
  },
  typography: {
    h4: {
      fontFamily: 'garamond-premier-pro',
      letterSpacing: '-0.5px'
    },
    h5: {
      fontFamily: 'garamond-premier-pro',
      fontSize: '1.75rem',
      letterSpacing: '-0.5px'
    },
    h6: {
      fontFamily: 'garamond-premier-pro',
      fontSize: '1.5rem'
    }
  }
})

export default MainTheme