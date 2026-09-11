import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import api
  from "../api/client";


const AuthContext =
  createContext(null);


export function AuthProvider({
  children,
}) {

  const [user, setUser] =
    useState(null);

  const [loading, setLoading] =
    useState(true);


  async function loadUser() {

    try {

      const response =
        await api.get(
          "/auth/me/"
        );


      setUser(
        response.data.data
      );

    } catch {

      setUser(null);

    } finally {

      setLoading(false);
    }
  }


  async function login(
    username,
    password
  ) {

    const response =
      await api.post(
        "/auth/login/",
        {
          username,
          password,
        }
      );


    localStorage.setItem(
      "access_token",
      response.data.access
    );


    localStorage.setItem(
      "refresh_token",
      response.data.refresh
    );


    await loadUser();
  }


  function logout() {

    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "refresh_token"
    );

    setUser(null);
  }


  useEffect(() => {

    if (
      localStorage.getItem(
        "access_token"
      )
    ) {

      loadUser();

    } else {

      setLoading(false);
    }

  }, []);


  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}


export function useAuth() {

  return useContext(
    AuthContext
  );
}