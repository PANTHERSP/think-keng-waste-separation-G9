import useImageStore from "./useImageStore";
import { useNavigate } from "react-router-dom";
import React, { useEffect, useState } from 'react';
import { io } from 'socket.io-client';


const RealtimeDetect = () => {
  const [videoSrc, setVideoSrc] = useState('');

  useEffect(() => {
    const socket = io('http://localhost:5501');

    socket.on('processed_frame', function (frameBase64) {
      console.log("Received frame");
      setVideoSrc('data:image/jpeg;base64,' + frameBase64.frame_base64);
    });

    // Cleanup เมื่อ component ถูก unmount
    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <div>
      <h1>Waste Segmentation</h1>
      <img
        id="video-frame"
        src={videoSrc}
        alt="Video Stream"
        style={{ width: '640px', height: '480px' }}
      />
    </div>
  );
};

export default RealtimeDetect;
