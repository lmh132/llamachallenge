// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBMVdcyfgPDWMZ-HCEPZ1Tuo7fwtS4E4K8",
  authDomain: "pathfinder-c8394.firebaseapp.com",
  projectId: "pathfinder-c8394",
  storageBucket: "pathfinder-c8394.firebasestorage.app",
  messagingSenderId: "889409827246",
  appId: "1:889409827246:web:4ab729037e832ab329583f",
  measurementId: "G-FT1S23TDKB"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);