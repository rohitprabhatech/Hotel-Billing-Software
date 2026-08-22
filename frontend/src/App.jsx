import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ColorModeProvider } from './context/ColorModeContext';
import { ModulesProvider } from './context/ModulesContext';
import AppRoutes from './routes/AppRoutes';

export default function App() {
  return (
    <ColorModeProvider>
      <AuthProvider>
        <ModulesProvider>
          <BrowserRouter>
            <AppRoutes />
          </BrowserRouter>
        </ModulesProvider>
      </AuthProvider>
    </ColorModeProvider>
  );
}
