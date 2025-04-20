import axios from 'axios';

const API_URL = 'http://localhost:8000'; // Replace with your API URL


export const login = async (uid: string) => {
    try {
        const response = await axios.get(`${API_URL}/getuser`, { params : {  user_id: uid }});
        return response.data;
    } catch (error) {
        console.error('Error logging in:', error);
        throw error;
    }
}

export const signup = async (user_data : any) => {
    try {
        console.log(user_data);
        const response = await axios.post(`${API_URL}/createuser`,  { ...user_data });
        return response.data;
    } catch (error) {
        console.error('Error signing up:', error);
        throw error;
    }
}

export const getGraphs = async (uid : string) => {
    try{
        const response = await axios.get(`${API_URL}/getusergraphs`, { params : {  user_id: uid }});
        return response.data;
    }
    catch (error) {
        console.error('Error getting graphs:', error);
        throw error;
    }
}

export const createGraph = async (graph_data : any) => {
    try{
        console.log(graph_data);
        const response = await axios.post(`${API_URL}/decomp`, { ...graph_data});
        return response.data;
    }
    catch (error) {
        console.error('Error getting graphs:', error);
        throw error;
    }
}