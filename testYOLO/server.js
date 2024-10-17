const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors'); // เพิ่มการเรียกใช้งาน cors

const app = express();
// const { spawn } = require('child_process');
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: '*', // หรือระบุโดเมนที่ต้องการอนุญาต
    methods: ['GET', 'POST']
  }
});

// ใช้ cors กับ express
app.use(cors());

io.on('connection', (socket) => {
  console.log('WebSocket client connected');

  // เรียกใช้ yolo.py เมื่อมีการเชื่อมต่อ
  // const pythonProcess = spawn('python', ['model.py']);

  // // pythonProcess.stdout.on('data', (data) => {
  // //   console.log(`Output from Python script: ${data}`);
  // // });

  // pythonProcess.stderr.on('data', (data) => {
  //   console.error(`Error from Python script: ${data}`);
  // });

  // pythonProcess.on('close', (code) => {
  //   console.log(`Python script exited with code ${code}`);
  // });
  

  socket.on('video_frame', (frame) => {
    // console.log("frame:", frame);
    io.emit('processed_frame', frame);
  });

  socket.on('disconnect', () => {
    console.log('WebSocket client disconnected');
    // if (pythonProcess) {
    //   pythonProcess.kill(); // หยุดกระบวนการ Python เมื่อ client หลุด
    // }
  });
});

const PORT = 5501;
server.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
