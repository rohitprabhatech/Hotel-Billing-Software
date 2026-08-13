import { Alert, Button, Stack, TextField, Typography } from '@mui/material';
import { useState } from 'react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  return (
    <Stack spacing={2} component="form" onSubmit={(e) => e.preventDefault()}>
      <Alert severity="info">
        Authentication arrives in Sprint 3. This login form is a UI placeholder.
      </Alert>
      <TextField
        label="Email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        fullWidth
        required
      />
      <TextField
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        fullWidth
        required
      />
      <Button type="submit" variant="contained" size="large">
        Sign in
      </Button>
      <Typography variant="caption" color="text.secondary">
        Roles in this version: Hotel Owner and Billing User only.
      </Typography>
    </Stack>
  );
}