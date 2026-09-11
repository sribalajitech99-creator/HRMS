import axios from "axios";


const api = axios.create({
  baseURL:
    import.meta.env.VITE_API_BASE_URL ||
    "http://127.0.0.1:8000/api/v1",
});


api.interceptors.request.use(
  (config) => {

    const token =
      localStorage.getItem(
        "access_token"
      );

    if (token) {

      config.headers.Authorization =
        `Bearer ${token}`;
    }

    return config;
  }
);


api.interceptors.response.use(
  (response) => response,

  async (error) => {

    const original =
      error.config;


    if (
      error.response?.status === 401 &&
      !original?._retry
    ) {

      original._retry = true;


      const refresh =
        localStorage.getItem(
          "refresh_token"
        );


      if (refresh) {

        try {

          const response =
            await axios.post(
              `${api.defaults.baseURL}/auth/refresh/`,

              {
                refresh,
              }
            );


          const access =
            response.data.access;


          localStorage.setItem(
            "access_token",
            access
          );


          original.headers.Authorization =
            `Bearer ${access}`;


          return api(
            original
          );

        } catch {

          localStorage.clear();

          window.location.href =
            "/login";
        }
      }
    }


    return Promise.reject(
      error
    );
  }
);


export default api;