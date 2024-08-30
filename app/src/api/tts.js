import axios from 'axios';

const TTS_API_ENDPOINT = `${process.env.REACT_APP_API_BASE_URL}/api/tts`;

export const getTextToSpeech = async (text) => {
  try {
    const response = await axios.post(TTS_API_ENDPOINT, { text });
    return response.data;
  } catch (error) {
    console.error('TTS API 请求失败:', error);
    throw error;
  }
};
