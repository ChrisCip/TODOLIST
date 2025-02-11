export interface ValidationError {
  loc: string[];
  msg: string;
  type: string;
}

export interface ApiError {
  detail?: string | ValidationError[];
  message?: string;
}
