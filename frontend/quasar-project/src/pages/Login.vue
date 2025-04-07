<template>
    <q-page class="flex flex-center login-page">
      <q-card class="q-pa-lg shadow-3 login-card">
        <q-card-section class="text-center">
          <q-avatar size="80px" class="bg-primary text-white">
            <q-icon name="inventory_2" size="50px" />
          </q-avatar>
          <div class="text-h5 text-primary q-mt-md">Inventory System</div>
          <div class="text-caption text-grey-7">Login to manage your stock & sales</div>
        </q-card-section>
  
        <q-card-section>
          <q-input
            v-model="username"
            label="Username"
            outlined
            dense
            :error="!username && submitted"
            error-message="Username is required"
          >
            <template v-slot:prepend>
              <q-icon name="person" />
            </template>
          </q-input>
  
          <q-input
            v-model="password"
            :type="isPwd ? 'password' : 'text'"
            label="Password"
            outlined
            dense
            class="q-mt-md"
            :error="!password && submitted"
            error-message="Password is required"
          >
            <template v-slot:prepend>
              <q-icon name="lock" />
            </template>
            <template v-slot:append>
              <q-btn flat dense round :icon="isPwd ? 'visibility' : 'visibility_off'" @click="isPwd = !isPwd" />
            </template>
          </q-input>
        </q-card-section>
  
        <q-card-section>
          <q-btn
            label="Login"
            color="primary"
            class="full-width"
            unelevated
            @click="login"
            :loading="loading"
          />
        </q-card-section>
      </q-card>
    </q-page>
  </template>
  
  <script setup>
  import { ref } from "vue";
  import { useRouter } from "vue-router";
  import { useQuasar } from "quasar";
  import { api } from "src/boot/axios";
  import { usePermissionStore } from 'src/stores/permission';
  const username = ref("");
  const password = ref("");
  const loading = ref(false);
  const isPwd = ref(true);
  const submitted = ref(false);
  
  const router = useRouter();
  const $q = useQuasar();
  const permission = usePermissionStore();
  
  const login = async () => {
    submitted.value = true;
  
    if (!username.value || !password.value) return;
  
    loading.value = true;
  
    try {
      const response = await api.post("login/", {
        username: username.value,
        password: password.value,
      });
  
      localStorage.setItem("token", response.data.token);
      localStorage.setItem("shop_name", response.data.shop_name || 'My Shop');
      localStorage.setItem("first_name", response.data.first_name || '');
      localStorage.setItem("last_name", response.data.last_name || '');
      localStorage.setItem("role", response.data.role);
      // Update Pinia store
    permission.setRole(response.data.role);


  
      $q.notify({ type: "positive", message: "Login successful!" });
//       // After setting all localStorage items in your login component
// window.dispatchEvent(new Event('storage'));
      router.push("/");
    } catch (error) {
      $q.notify({ type: "negative", message: "Invalid credentials." });
    } finally {
      loading.value = false;
    }
  };
  </script>
  
  <style scoped>
  .login-page {
    background: linear-gradient(to right, #4facfe, #00f2fe);
    min-height: 100vh;
    padding: 16px;
  }
  
  .login-card {
    width: 100%;
    max-width: 400px;
    border-radius: 12px;
    background: white;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  .q-avatar {
    margin: auto;
  }
  
  /* Mobile devices (portrait) */
  @media (max-width: 599px) {
    .login-card {
      width: 100%;
      padding: 20px;
    }
    
    .text-h5 {
      font-size: 1.25rem;
    }
    
    .q-avatar {
      width: 60px;
      height: 60px;
    }
    
    .q-icon[name="inventory_2"] {
      font-size: 40px;
    }
  }
  
  /* Small tablets (portrait) */
  @media (min-width: 600px) and (max-width: 767px) {
    .login-card {
      width: 80%;
      padding: 24px;
    }
  }
  
  /* Tablets and small desktops */
  @media (min-width: 768px) and (max-width: 1023px) {
    .login-card {
      width: 65%;
    }
  }
  
  /* Large tablets and desktops */
  @media (min-width: 1024px) {
    .login-card {
      width: 400px;
    }
  }
  
  /* Extra small devices (like iPhone 5) */
  @media (max-width: 320px) {
    .login-card {
      padding: 16px;
    }
    
    .text-h5 {
      font-size: 1.1rem;
    }
    
    .text-caption {
      font-size: 0.7rem;
    }
    
    .q-field {
      margin-bottom: 12px;
    }
  }
  
  /* Landscape orientation */
  @media (max-height: 500px) {
    .login-page {
      min-height: 120vh;
      padding-top: 20px;
      padding-bottom: 20px;
    }
  }
  </style>