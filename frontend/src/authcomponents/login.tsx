/**
 * Login Component
 * 
 * This component handles user authentication through a login form.
 * It uses Chakra UI for styling and React Router for navigation.
 */

import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
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
import { api } from "../api/axios";

interface LoginFormData {
  email: string;
  password: string;
}

export default function Login() {
  // Hooks for navigation and authentication
  const navigate = useNavigate();
  const { login } = useAuth();

  // State management
  const [error, setError] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  /**
   * Handles form submission for user login
   * @param e - Form submission event
   */
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    const formData = new FormData(e.currentTarget);
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;

    try {
      const response = await api.post('/auth/login', 
        new URLSearchParams({
          username: email,
          password: password,
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      login(response.data.access_token, { email, _id: "", name: "" });
      navigate("/tasks");
    } catch (err) {
      setError("Invalid email or password");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxW="container.sm" py={10}>
      <Card>
        <CardHeader>
          <Heading size="lg" textAlign="center">Welcome Back</Heading>
        </CardHeader>
        <CardBody>
          <form onSubmit={handleSubmit}>
            <VStack spacing={4}>  {/* Using spacing instead of gap for Chakra UI */}
              {/* Error Alert */}
              {error && (
                <Alert status="error">
                  <AlertIcon />
                  {error}
                </Alert>
              )}

              {/* Email Input */}
              <FormControl isRequired>
                <FormLabel>Email</FormLabel>
                <Input
                  name="email"
                  type="email"
                  placeholder="your@email.com"
                />
              </FormControl>

              {/* Password Input */}
              <FormControl isRequired>
                <FormLabel>Password</FormLabel>
                <Input
                  name="password"
                  type="password"
                  placeholder="********"
                />
              </FormControl>

              {/* Submit Button */}
              <Button
                type="submit"
                colorScheme="blue"
                width="full"
                isLoading={isLoading}  // Changed from loading to isLoading
              >
                Sign In
              </Button>

              {/* Registration Link */}
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
