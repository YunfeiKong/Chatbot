import axios from 'axios';

const ASR_API_ENDPOINT = `${process.env.REACT_APP_API_BASE_URL}/api/asr`;

export const sendAudioToASR = async (audioBlob, history) => {
  const formData = new FormData();
  formData.append('audio', audioBlob);
  formData.append('history', history);

  try {
    const response = await axios.post(ASR_API_ENDPOINT, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('ASR API 请求失败:', error);
    throw error;
  }
};
