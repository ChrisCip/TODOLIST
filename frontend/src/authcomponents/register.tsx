import { useState } from "react";
interface ValidationError {
  loc: string[];
  msg: string;
  type: string;
}
import { useNavigate } from "react-router-dom";
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
  useToast,
} from "@chakra-ui/react";
import { Link } from "react-router-dom";
import { api } from "../api/api";

console.log('API URL:', import.meta.env.BACKEND_URL + '/auth/signup');

interface FormErrors {
  name?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  general?: string;
}

export default function Register() {
  const navigate = useNavigate();
  const toast = useToast();
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrors({});
    setIsLoading(true);

    const formData = new FormData(e.currentTarget);
    const name = formData.get("name") as string;
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;
    const confirmPassword = formData.get("confirmPassword") as string;

    if (password !== confirmPassword) {
      setErrors({ confirmPassword: "Passwords do not match" });
      setIsLoading(false);
      return;
    }

    try {
      await api.post('/auth/signup', {
        name,
        email,
        password,
      });

      toast({
        title: "Success!",
        description: "Account created successfully.",
        status: "success",
        duration: 3000,
      });
      
      navigate("/login");
    } catch (err: any) {
      const response = err.response?.data;
      
      // Handle validation errors from FastAPI
      if (err.response?.status === 422 && Array.isArray(response?.detail)) {
        const newErrors: FormErrors = {};
        response.detail.forEach((error: ValidationError) => {
          const field = error.loc[1];
          newErrors[field as keyof FormErrors] = error.msg;
        });
        setErrors(newErrors);
      } 
      // Handle duplicate email
      else if (err.response?.status === 400) {
        setErrors({ email: response?.message || "Email already registered" });
      }
      // Handle other errors
      else {
        setErrors({ 
          general: response?.message || "An error occurred during registration" 
        });
      }

      toast({
        title: "Registration failed",
        description: errors.general || "Please check the form for errors",
        status: "error",
        duration: 5000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxW="container.sm" py={10}>
      <Card>
        <CardHeader>
          <Heading size="lg" textAlign="center">Create Account</Heading>
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
              <FormControl isRequired isInvalid={!!errors.name}>
                <FormLabel>Name</FormLabel>
                <Input
                  name="name"
                  placeholder="John Doe"
                />
                {errors.name && (
                  <Alert status="error" mt={2} p={2} size="sm">
                    <AlertIcon />
                    {errors.name}
                  </Alert>
                )}
              </FormControl>
              <FormControl isRequired isInvalid={!!errors.email}>
                <FormLabel>Email</FormLabel>
                <Input
                  name="email"
                  type="email"
                  placeholder="john@example.com"
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
                  placeholder="********"
                />
                {errors.password && (
                  <Alert status="error" mt={2} p={2} size="sm">
                    <AlertIcon />
                    {errors.password}
                  </Alert>
                )}
              </FormControl>
              <FormControl isRequired isInvalid={!!errors.confirmPassword}>
                <FormLabel>Confirm Password</FormLabel>
                <Input
                  name="confirmPassword"
                  type="password"
                  placeholder="********"
                />
                {errors.confirmPassword && (
                  <Alert status="error" mt={2} p={2} size="sm">
                    <AlertIcon />
                    {errors.confirmPassword}
                  </Alert>
                )}
              </FormControl>
              <Button
                type="submit"
                colorScheme="blue"
                width="full"
                isLoading={isLoading}
              >
                Register
              </Button>
              <Text fontSize="sm">
                Already have an account?{" "}
                <Link to="/login" style={{ color: "blue" }}>
                  Login here
                </Link>
              </Text>
            </VStack>
          </form>
        </CardBody>
      </Card>
    </Container>
  );
}

