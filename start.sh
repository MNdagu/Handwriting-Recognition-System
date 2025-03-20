#!/bin/bash

# Start the backend server
cd backend
python3 manage.py migrate
python3 manage.py runserver &
BACKEND_PID=$!

# Start the frontend server
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID 