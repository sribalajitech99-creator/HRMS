import {
  useState,
} from "react";

import {
  useNavigate,
} from "react-router-dom";

import {
  LockKeyhole,
  ShieldCheck,
  User,
} from "lucide-react";

import {
  useAuth,
} from "../../context/AuthContext";

import "../../styles/login.css";


function Login() {

  const navigate =
    useNavigate();

  const {
    login,
  } = useAuth();


  const [
    username,
    setUsername
  ] = useState("");


  const [
    password,
    setPassword
  ] = useState("");


  const [
    error,
    setError
  ] = useState("");


  const [
    loading,
    setLoading
  ] = useState(false);


  async function submit(
    event
  ) {

    event.preventDefault();

    setLoading(true);

    setError("");


    try {

      await login(
        username,
        password
      );

      navigate(
        "/dashboard"
      );

    } catch {

      setError(
        "Invalid username or password."
      );

    } finally {

      setLoading(false);
    }
  }


  return (
    <div className="container-fluid min-vh-100 p-0">

      <div className="row g-0 min-vh-100">

        <div className="col-lg-6 d-none d-lg-flex align-items-center justify-content-center login-brand-panel">

          <div className="login-brand-content">

            <div className="login-logo-box mb-4">

              <ShieldCheck
                size={34}
              />

            </div>


            <h1 className="login-brand-title">

              Enterprise HRMS

            </h1>


            <p className="login-brand-subtitle">

              People, attendance,
              leave, payroll,
              recruitment and
              workforce operations
              in one secure platform.

            </p>

          </div>

        </div>


        <div className="col-lg-6 d-flex align-items-center justify-content-center bg-white">

          <div className="login-form-wrapper">

            <h2 className="login-heading">

              Welcome Back

            </h2>


            <p className="login-description">

              Sign in to continue.

            </p>


            {error && (

              <div className="alert alert-danger">

                {error}

              </div>

            )}


            <form
              onSubmit={submit}
            >

              <label className="form-label">

                Username

              </label>


              <div className="input-group mb-3">

                <span className="input-group-text">

                  <User
                    size={18}
                  />

                </span>


                <input
                  className="form-control"

                  value={
                    username
                  }

                  onChange={
                    (e) =>
                      setUsername(
                        e.target.value
                      )
                  }

                  required
                />

              </div>


              <label className="form-label">

                Password

              </label>


              <div className="input-group mb-4">

                <span className="input-group-text">

                  <LockKeyhole
                    size={18}
                  />

                </span>


                <input
                  type="password"

                  className="form-control"

                  value={
                    password
                  }

                  onChange={
                    (e) =>
                      setPassword(
                        e.target.value
                      )
                  }

                  required
                />

              </div>


              <button
                className="btn btn-primary w-100 login-button"

                disabled={
                  loading
                }
              >

                {
                  loading
                    ? "Signing In..."
                    : "Sign In"
                }

              </button>

            </form>

          </div>

        </div>

      </div>

    </div>
  );
}


export default Login;