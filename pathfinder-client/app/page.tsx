'use client';
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useContext, useEffect } from "react";
import { AuthContext } from "../contexts/AuthContext";

export default function Home() {
  const router = useRouter();
  const { user, loading } = useContext(AuthContext);

  useEffect(() => {
  if (user){
      router.push("/home");
    }
    else{
      router.push("/login");
    }
  }, [user, loading, router]);
  return (
    <>  
      {loading ? <div>Loading...</div> : user ? <div>User is logged in</div> : <div>User is not logged in</div>}
    </>
  );
}
