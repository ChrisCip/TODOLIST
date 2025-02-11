/**
 * Login Component
 * 
 * This component handles user authentication through a login form.
 * It uses Chakra UI for styling and React Router for navigation.
 */

import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ValidationError } from "../types/errors";
import {
  Button,
  Card,
  CardBody,
  CardHeader,
  FormControl,
  FormLabel,
  Input,
  Text,
  VStack,
  Alert,
  AlertIcon,
  Container,
  Heading,
} from "@chakra-ui/react";
import { api } from "../api/api";

interface FormErrors {
  email?: string;
  password?: string;
  general?: string;
}

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrors({});
    setIsLoading(true);

    try {
      const response = await api.post('/auth/login', 
        new URLSearchParams({
          username: formData.email,
          password: formData.password,
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      login(response.data.access_token, { email: formData.email, _id: "", name: "" });
      navigate("/tasks");
    } catch (err: any) {
      const response = err.response?.data;
      
      if (err.response?.status === 401) {
        setErrors({ 
          general: "Invalid email or password" 
        });
      } else if (err.response?.status === 422 && Array.isArray(response?.detail)) {
        const newErrors: FormErrors = {};
        response.detail.forEach((error: ValidationError) => {
          const field = error.loc[1];
          newErrors[field as keyof FormErrors] = error.msg;
        });
        setErrors(newErrors);
      } else {
        setErrors({ 
          general: response?.message || "Login failed. Please try again." 
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxW="container.sm" py={10}>
      <Card>
        <CardHeader>
          <Heading size="lg" textAlign="center">TODO APP</Heading>
        </CardHeader>
        <CardBody>
          <form onSubmit={handleSubmit}>
            <VStack spacing={4}>
              {errors.general && (
                <Alert status="error">
                  <AlertIcon />
                  {errors.general}
                </Alert>
              )}

              <FormControl isRequired isInvalid={!!errors.email}>
                <FormLabel>Email</FormLabel>
                <Input
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="your@email.com"
                />
                {errors.email && (
                  <Alert status="error" mt={2} p={2} size="sm">
                    <AlertIcon />
                    {errors.email}
                  </Alert>
                )}
              </FormControl>

              <FormControl isRequired isInvalid={!!errors.password}>
                <FormLabel>Password</FormLabel>
                <Input
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="********"
                />
                {errors.password && (
                  <Alert status="error" mt={2} p={2} size="sm">
                    <AlertIcon />
                    {errors.password}
                  </Alert>
                )}
              </FormControl>

              <Button
                type="submit"
                colorScheme="blue"
                width="full"
                isLoading={isLoading}
              >
                Sign In
              </Button>

              <Text fontSize="sm">
                Don't have an account?{" "}
                <Link to="/register" style={{ color: "blue" }}>
                  Register here
                </Link>
              </Text>
            </VStack>
          </form>
        </CardBody>
      </Card>
    </Container>
  );
}
