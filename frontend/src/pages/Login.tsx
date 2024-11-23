import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/useAuth';
import {
  Card,
  CardBody,
  Typography,
  Button,
} from "@material-tailwind/react";

const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  // Social Media Icon Components (reuse your existing ones)
  const GoogleIcon = () => (
    <svg viewBox="0 0 24 24" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
      <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
      <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
      <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
      <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
    </svg>
  );

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <Typography variant="h2" className="text-gray-900">
            Log in to your account
          </Typography>
        </div>

        <Card className="bg-white shadow-md">
          <CardBody className="flex flex-col gap-6 p-6">
            <Button
              onClick={() => login()}
              className="bg-blue-600 hover:bg-blue-700 w-full"
              size="lg"
            >
              Continue with Auth0
            </Button>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="bg-white px-4 text-gray-500">or continue with</span>
              </div>
            </div>

            <Button
              variant="outlined"
              color="blue-gray"
              className="flex items-center justify-center gap-2 normal-case text-sm font-normal"
              onClick={() => login()}
            >
              <GoogleIcon />
              Google
            </Button>
          </CardBody>
        </Card>
      </div>
    </div>
  );
};

export default LoginPage;