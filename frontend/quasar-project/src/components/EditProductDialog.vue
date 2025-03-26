<template>
    <q-dialog v-model="modelValue">
      <q-card style="width: 400px">
        <q-card-section>
          <div class="text-h6">Edit Product</div>
        </q-card-section>
  
        <q-card-section>
          <q-input v-model="form.name" label="Product Name" outlined dense />
          <q-input v-model="form.category" label="Category" outlined dense />
          <q-input v-model.number="form.price" label="Price" type="number" outlined dense />
          <q-input v-model.number="form.quantity" label="Quantity" type="number" outlined dense />
        </q-card-section>
  
        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="negative" v-close-popup />
          <q-btn label="Save" color="primary" @click="updateProduct" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </template>
  
  <script setup>
  import { ref, defineProps, defineEmits, watch } from 'vue';
  import { useQuasar } from 'quasar';
  import { api } from 'src/boot/axios';
  
  const $q = useQuasar();
  const emit = defineEmits(['refresh']);
  const props = defineProps(['modelValue', 'product']);
  
  const form = ref({
    id: null,
    name: '',
    category: '',
    price: 0,
    quantity: 1
  });
  
  watch(() => props.product, (newProduct) => {
    if (newProduct) {
      form.value = { ...newProduct };
    }
  }, { immediate: true });
  
  const updateProduct = async () => {
    try {
      await api.put(`products/${form.value.id}/`, form.value);
      $q.notify({ message: 'Product updated', color: 'positive', icon: 'check' });
      emit('refresh');
    } catch (error) {
      $q.notify({ message: 'Error updating product', color: 'negative', icon: 'error' });
    }
  };
  </script>
  