import { useState, useEffect } from "react";
import {
  Box,
  Container,
  Heading,
  Button,
  VStack,
  HStack,
  Text,
  Input,
  Textarea,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  FormControl,
  FormLabel,
  IconButton,
  Card,
  CardBody,
} from "@chakra-ui/react";
import { DeleteIcon, EditIcon } from "@chakra-ui/icons";
import { Task, TaskCreate } from "../types/task";
import { api } from "../api/axios";
import { useAuth } from "../context/AuthContext";

export default function TaskList() {
  const { logout } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [newTask, setNewTask] = useState<TaskCreate>({
    title: "",
    description: "",
  });

  const fetchTasks = async () => {
    try {
      const response = await api.get<Task[]>("/tasks");
      setTasks(response.data);
    } catch (error) {
      console.error("Error fetching tasks:", error);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleEditTask = (task: Task) => {
    setSelectedTask(task);
    setNewTask({
      title: task.title,
      description: task.description || "",
    });
    onOpen();
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      if (selectedTask) {
        await api.put(`/tasks/${selectedTask._id}`, newTask);
      } else {
        await api.post("/tasks", newTask);
      }
      setNewTask({ title: "", description: "" });
      setSelectedTask(null);
      fetchTasks();
      onClose();
    } catch (error) {
      console.error("Error creating/updating task:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      await api.delete(`/tasks/${taskId}`);
      fetchTasks();
    } catch (error) {
      console.error("Error deleting task:", error);
    }
  };

  return (
    <Container maxW="container.md" py={8}>
      <VStack spacing={6} align="stretch">
        <HStack justify="space-between">
          <Heading size="lg">My Tasks</Heading>
          <HStack spacing={4}>
            <Button colorScheme="blue" onClick={onOpen}>
              Add Task
            </Button>
            <Button colorScheme="red" variant="outline" onClick={logout}>
              Logout
            </Button>
          </HStack>
        </HStack>

        {tasks.map((task) => (
          <Card key={task._id}>
            <CardBody>
              <HStack justify="space-between">
                <Box>
                  <Text fontSize="lg">
                    {task.title}
                  </Text>
                  {task.description && (
                    <Text color="gray.600" fontSize="sm">
                      {task.description}
                    </Text>
                  )}
                </Box>
                <HStack>
                  <IconButton
                    aria-label="Edit task"
                    icon={<EditIcon />}
                    colorScheme="blue"
                    variant="ghost"
                    onClick={() => handleEditTask(task)}
                  />
                  <IconButton
                    aria-label="Delete task"
                    icon={<DeleteIcon />}
                    colorScheme="red"
                    variant="ghost"
                    onClick={() => handleDeleteTask(task._id)}
                  />
                </HStack>
              </HStack>
            </CardBody>
          </Card>
        ))}

        <Modal isOpen={isOpen} onClose={onClose}>
          <ModalOverlay />
          <ModalContent>
            <form onSubmit={handleCreateTask}>
              <ModalHeader>
                {selectedTask ? "Edit Task" : "Create New Task"}
              </ModalHeader>
              <ModalCloseButton />
              <ModalBody>
                <VStack spacing={4}>
                  <FormControl isRequired>
                    <FormLabel>Title</FormLabel>
                    <Input
                      value={newTask.title}
                      onChange={(e) =>
                        setNewTask({ ...newTask, title: e.target.value })
                      }
                      placeholder="Task title"
                    />
                  </FormControl>
                  <FormControl>
                    <FormLabel>Description</FormLabel>
                    <Textarea
                      value={newTask.description}
                      onChange={(e) =>
                        setNewTask({ ...newTask, description: e.target.value })
                      }
                      placeholder="Task description (optional)"
                    />
                  </FormControl>
                </VStack>
              </ModalBody>
              <ModalFooter>
                <Button variant="ghost" mr={3} onClick={onClose}>
                  Cancel
                </Button>
                <Button
                  colorScheme="blue"
                  type="submit"
                  isLoading={isLoading}
                >
                  {selectedTask ? "Save Changes" : "Create Task"}
                </Button>
              </ModalFooter>
            </form>
          </ModalContent>
        </Modal>
      </VStack>
    </Container>
  );
} 