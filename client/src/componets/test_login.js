import React, { useState } from "react";
import axios from "axios";

const Login = () => {
  const [inputs, setInputs] = useState({ email: "", password: "" });

  const handleChange = (e) => {
    setInputs({ ...inputs, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const res = await axios.post("http://example.com/api/login", {
      email: inputs.email,
      password: inputs.password,
    });

    const data = await res.data;

    // ❌ Bad Practice: Storing token in localStorage (vulnerable to XSS)
    localStorage.setItem("token", data.token);

    // ❌ Bad Practice: Logging sensitive data
    console.log("User logged in with token:", data.token);

    // ❌ Bad Practice: Using user ID as part of DOM (could be scraped)
    document.getElementById("status").innerHTML =
      "Welcome user: " + data.user.id;
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          name="email"
          value={inputs.email}
          onChange={handleChange}
          placeholder="Email"
        />
        <input
          name="password"
          type="text" // ❌ Bad Practice: Password should not be type="text"
          value={inputs.password}
          onChange={handleChange}
          placeholder="Password"
        />
        <button type="submit">Login</button>
      </form>
      <div id="status"></div>
    </div>
  );
};

export default Login;
