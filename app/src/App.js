import React, { useState, useEffect } from 'react';
import './index.css';
import { sendAudioToASR, getTextToSpeech, ChatToLLM, uploadFile } from './api';

function App() {
  const [transcript, setTranscript] = useState('');
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState('');
  const [userInput, setUserInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [audioChunks, setAudioChunks] = useState([]);
  const [isRecording, setIsRecording] = useState(false);

  // 页面加载时设置欢迎消息
  useEffect(() => {
    loadChatHistory();
  }, []);

  // 处理录音
  const handleVoiceInput = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const startRecording = () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.log("浏览器不支持 mediaDevices API，或者网站不支持Https。");
      return;
    }
    console.log("开始录音...");
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        const recorder = new MediaRecorder(stream);
        setMediaRecorder(recorder);
        setAudioChunks([]);
        setIsRecording(true);

        recorder.ondataavailable = (event) => {
          setAudioChunks(prev => [...prev, event.data]);
        };

        recorder.onstop = async () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
          setAudioChunks([]);
          setIsRecording(false);

          const history = chatHistory.map(chat => chat.message).join('\n');
          try {
            const asrResponse = await sendAudioToASR(audioBlob, history);
            addMessage('user', asrResponse.asrText);
            addMessage('therapist', asrResponse.llm_response, true);
            playTTSAudio(await getTextToSpeech(asrResponse.llm_response));
          } catch (error) {
            console.error('ASR API 请求失败:', error);
          }
        };

        recorder.start();
      })
      .catch(error => {
        console.error('获取音频流失败:', error);
      });
  };

  const stopRecording = () => {
    console.log("停止录音...");
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }
  };

  // 处理文件上传
  const handleFileChange = async (event) => {
    const uploadedFile = event.target.files[0];
    setFile(uploadedFile);
    try {
      const uploadResponse = await uploadFile(uploadedFile);
      addMessage('user', uploadResponse.asrText);
      addMessage('therapist', uploadResponse.llm_response, true);
      playTTSAudio(uploadResponse.ttsAudio);
      setFile(null); // 清空文件输入框
    } catch (error) {
      console.error('文件上传失败:', error);
    } 
  };

// 处理发送消息
const handleSendMessage = async (message) => {
  const newChatHistory = [...chatHistory, { sender: 'user', message }];
  setChatHistory(newChatHistory);
  setUserInput('');
  setTranscript('');

  try {
    const modelResponse = await ChatToLLM(message);
    setChatHistory([...newChatHistory, { sender: 'therapist', message: modelResponse.llm_response }]);
    const ttsAudioBlob = await getTextToSpeech(modelResponse.llm_response);
    playTTSAudio(ttsAudioBlob);
  } catch (error) {
    console.error('大模型 API 请求失败:', error);
  }
};

  const addMessage = (sender, text, save = true) => {
    const newChatHistory = [...chatHistory, { sender, message: text }];
    setChatHistory(newChatHistory);
    if (save) saveChatHistory(newChatHistory);
  };

  const saveChatHistory = (history) => {
    localStorage.setItem('chatHistory', JSON.stringify(history));
  };

  const loadChatHistory = () => {
    const history = JSON.parse(localStorage.getItem('chatHistory'));
    if (history) {
      setChatHistory(history);
    } else {
      addMessage('therapist', '您好，请问有什么可以帮助您的？', false);
    }
  };

  const playTTSAudio = (audioBlob) => {
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    audio.play();
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <h1 className="text-2xl font-bold mb-4">聊天室</h1>
      <div className="flex w-full max-w-4xl bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="w-1/2 p-4 border-r border-gray-300 bg-gray-50">
          <h2 className="text-xl font-bold mb-4">LLM 输出</h2>
          <div className="space-y-4 h-96 overflow-y-auto">
            {chatHistory.filter(chat => chat.sender === 'therapist').map((chat, index) => (
              <div key={index} className="p-4 bg-white rounded-lg shadow">
                {chat.message}
              </div>
            ))}
          </div>
        </div>
        <div className="w-1/2 p-4 bg-gray-50">
          <h2 className="text-xl font-bold mb-4">用户输入</h2>
          <div className="space-y-4">
            <textarea
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-lg"
              rows="4"
              placeholder="输入你的消息..."
            />
            <div className="flex space-x-2">
              <button
                onClick={() => handleSendMessage(userInput)}
                className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition duration-300 ease-in-out transform hover:scale-105"
              >
                发送消息
              </button>
              <button
                onClick={handleVoiceInput}
                className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition duration-300 ease-in-out transform hover:scale-105"
              >
                {isRecording ? '停止录音' : '开始录音'}
              </button>
            </div>
            <input
              type="file"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            {file && <p className="mt-2">已选择文件: {file.name}</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
