export interface Task {
  _id: string;
  user_id: string;
  title: string;
  description?: string;
  due_date?: string;
  created_at: string;
  updated_at?: string;
  completed: boolean;
}

export interface TaskCreate {
  title: string;
  description?: string;
  due_date?: string;
} 