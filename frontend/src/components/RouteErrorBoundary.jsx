import { Alert, Box, Button, Stack, Typography } from '@mui/material';
import { Component } from 'react';

/**
 * Catches render errors in a route subtree so one page crash does not blank the whole shell.
 */
export default class RouteErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.error('RouteErrorBoundary caught:', error, info);
    }
  }

  handleRetry = () => {
    this.setState({ error: null });
  };

  render() {
    if (this.state.error) {
      return (
        <Box sx={{ p: { xs: 2, sm: 3 }, maxWidth: 560 }}>
          <Alert severity="error" sx={{ mb: 2 }}>
            Something went wrong on this page.
          </Alert>
          <Stack spacing={1.5}>
            <Typography variant="body2" color="text.secondary">
              The rest of the app is still available. You can try again or open another page from
              the menu.
            </Typography>
            <Button variant="contained" onClick={this.handleRetry} sx={{ alignSelf: 'flex-start' }}>
              Try again
            </Button>
          </Stack>
        </Box>
      );
    }
    return this.props.children;
  }
}
