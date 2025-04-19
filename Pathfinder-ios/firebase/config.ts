import auth from '@react-native-firebase/auth';
import { initializeApp } from '@react-native-firebase/app';

const firebaseConfig = {
  // Copy this from your Firebase Console 
  apiKey: process.env.API_KEY,
  authDomain: process.env.AUTH_DOMAIN,
  projectId: process.env.PROJECT_ID,
  storageBucket: process.env.STORAGE_BUCKET,
  messagingSenderId: process.env.GCM_SENDER_ID,
  appId: process.env.GOOGLE_APP_ID
};

initializeApp(firebaseConfig);

export { auth };
