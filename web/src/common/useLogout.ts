import router from "../router";

export default function logout() {
  localStorage.removeItem("access_token");
  router.push("/login");
}
