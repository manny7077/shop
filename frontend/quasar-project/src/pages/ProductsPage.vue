<script setup>
import { ref, onMounted, computed } from 'vue';
import { useQuasar } from 'quasar';
import { api } from 'src/boot/axios';
import SaleDialog from 'src/components/SaleDialog.vue';

const $q = useQuasar();

const columns = [
  { name: 'name', label: 'Product Name', field: 'name', sortable: true, align: 'left' },
  { name: 'category', label: 'Category',  field: row => row.category?.name || 'N/A', sortable: true, align: 'left' },
  { 
    name: 'price', 
    label: 'Price (GHS)', 
    field: row => `GHS ${(Number(row.price) || 0).toFixed(2)}`,
    sortable: true, 
    align: 'left' 
  },
  { name: 'quantity', label: 'Quantity', field: 'quantity', sortable: true, align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' }
];

const products = ref([]);
const filter = ref(null);

const showAddDialog = ref(false);
const showEditDialog = ref(false);
const showDeleteDialog = ref(false);
const selectedProduct = ref(null);
const selectedProductId = ref(null);
const newProduct = ref({ name: '', category: '', price: '', quantity: '' });
const showSaleDialog = ref(false);
const totalRevenue = ref(0);
const bestSellingProducts = ref([]);
const salesCounts = ref({ daily_sales: 0, weekly_sales: 0, monthly_sales: 0 });

const fetchSalesSummary = async () => {
  try {


    // Fetch sales counts (daily, weekly, monthly)
    const salesCountsResponse = await api.get("sales/counts/");
    salesCounts.value = salesCountsResponse.data || { daily_sales: 0, weekly_sales: 0, monthly_sales: 0 };
  } catch (error) {
    console.error("Error fetching sales summary:", error);
  }
};



const fetchProducts = async () => {
  try {
    const response = await api.get("products/");
    products.value = response.data;
  } catch (error) {

  }
};


const openSaleDialog = (product) => {
  selectedProduct.value = product;
  showSaleDialog.value = true;
};


const editProduct = (product) => {
  selectedProduct.value = { 
    ...product, 
    category: product.category.id // Ensure it stores only the ID
  };
  showEditDialog.value = true;
};


const categories = ref([]); // Store available categories

const fetchCategories = async () => {
  try {
    const response = await api.get("categories/");
    categories.value = response.data;
  } catch (error) {
   
  }
};






const deleteProduct = (id) => {
  selectedProductId.value = id;
  showDeleteDialog.value = true;
};

const addProduct = async () => {
  if (!newProduct.value.name || !newProduct.value.category || !newProduct.value.price || !newProduct.value.quantity) {
    $q.notify({
      type: 'warning',
      message: 'All fields are required!',
    });
    return;
  }

  try {
    await api.post("products/add/", newProduct.value);
    fetchProducts();
    showAddDialog.value = false;
  } catch (error) {
    $q.notify({ type: 'negative', message: 'Error adding product.' });
    console.error(error);
  }
};


const updateProduct = async () => {
  if (!selectedProduct.value.name || !selectedProduct.value.category || !selectedProduct.value.price || !selectedProduct.value.quantity) {
    $q.notify({ type: 'warning', message: 'All fields are required!' });
    return;
  }

  try {
    await api.put(`products/edit/${selectedProduct.value.id}/`, {
      ...selectedProduct.value,
      category: selectedProduct.value.category, // Already stored as an ID
    });
    showEditDialog.value = false;
    fetchProducts();
  } catch (error) {
    $q.notify({ type: 'negative', message: 'Error updating product.' });
    console.error(error);
  }
};




const confirmDelete = async () => {

  await api.delete(`products/delete/${selectedProductId.value}/`);
  showDeleteDialog.value = false;
  fetchProducts();
};


onMounted(() => {
  fetchProducts();  // Fetch products
  fetchCategories(); // Fetch categories
  fetchSalesSummary();
});
</script>

<template>

    <div class="q-pa-md">
  <!-- Sales Summary Cards -->
  <div class="q-my-md q-gutter-md row justify-between">
      <q-card v-for="(stat, index) in [

        { title: 'Today\'s Sales', value:   `GHS ${salesCounts.daily_sales.toFixed(2)}`, color: 'green' },
        { title: 'Weekly Sales', value: `GHS ${salesCounts.weekly_sales.toFixed(2)}`, color: 'blue' },
        { title: 'Monthly Sales', value: `GHS ${salesCounts.monthly_sales.toFixed(2)}`, color: 'orange' }
      ]" :key="index" class="col-12 col-md shadow-1 q-py-md sales-card">
        <q-card-section :class="`bg-${stat.color} text-white`">
          <div class="text-h6">{{ stat.title }}</div>
        </q-card-section>
        <q-card-section>
          <div class="text-h5">{{ stat.value }}</div>
        </q-card-section>
      </q-card>
    </div>


    
    <q-toolbar class="text-primary q-pb-md">
      <q-btn flat round dense icon="inventory_2" />
      <q-toolbar-title>
        <span class="text-weight-bold">Product Inventory</span>
      </q-toolbar-title>
      <q-space />
      <q-input outlined dense debounce="300" v-model="filter" placeholder="Search">
        <template v-slot:append>
          <q-icon name="search" />
        </template>
      </q-input>
    </q-toolbar>

    <div class="row q-gutter-sm">
  <q-btn color="primary" label="Add Product" icon="add" @click="showAddDialog = true" class="q-mb-md" />
  <q-btn 
    color="primary" 
    label="Sell Product" 
    icon="shopping_cart" 
    :disable="products.length === 0"
    @click="openSaleDialog(products[0])"
    class="q-mb-md"
  />
</div>




    <q-table :rows="products" :columns="columns" row-key="id" :filter="filter" class="custom-table">
      <template v-slot:body="props">
        <q-tr :props="props">
          <q-td v-for="col in props.cols" :key="col.name">
            <template v-if="col.name === 'actions'">
              <div class="action-buttons">
                <q-btn color="primary" dense flat icon="edit" @click="editProduct(props.row)" />
                <q-btn color="negative" dense flat icon="delete" @click="deleteProduct(props.row.id)" />
              </div>
            </template>
            <template v-else>
              {{ col.value }}
            </template>
          </q-td>
        </q-tr>
      </template>
    </q-table>
  </div>

  <!-- Add Product Dialog -->
<q-dialog v-model="showAddDialog">
  <q-card class="q-pa-md q-dialog-card">
    <q-card-section>
      <div class="text-h6 text-primary">Add Product</div>
    </q-card-section>
    <q-card-section>
      <q-form @submit="addProduct">
        <q-input v-model="newProduct.name" label="Product Name" dense outlined class="q-mb-md" />
        <q-select 
            v-model="newProduct.category" 
            label="Category" 
            :options="categories.map(c => ({ label: c.name, value: c.id }))"
            option-value="value" 
            option-label="label"
            emit-value
            map-options
            outlined
            class="q-mb-md"
            />

        <q-input v-model="newProduct.price" label="Price" type="number" dense outlined class="q-mb-md" prefix="GHS " />
        <q-input v-model="newProduct.quantity" label="Quantity" type="number" dense outlined class="q-mb-md" />
        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="grey" v-close-popup />
          <q-btn type="submit" label="Add" color="primary" />
        </q-card-actions>
      </q-form>
    </q-card-section>
  </q-card>
</q-dialog>

<!-- Edit Product Dialog -->
<q-dialog v-model="showEditDialog">
  <q-card class="q-pa-md q-dialog-card">
    <q-card-section>
      <div class="text-h6 text-primary">Edit Product</div>
    </q-card-section>
    <q-card-section>
      <q-form @submit="updateProduct">
        <q-input v-model="selectedProduct.name" label="Product Name" dense outlined class="q-mb-md" />
        <q-select 
  v-model="selectedProduct.category"
  label="Category"
  :options="categories.map(c => ({ label: c.name, value: c.id }))"
  option-value="value"
  option-label="label"
  emit-value
  map-options
  outlined
  class="q-mb-md"
/>


        <q-input v-model="selectedProduct.price" label="Price" type="number" dense outlined class="q-mb-md" prefix="GHS " />
        <q-input v-model="selectedProduct.quantity" label="Quantity" type="number" dense outlined class="q-mb-md" />
        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="grey" v-close-popup />
          <q-btn type="submit" label="Save Changes" color="primary" />
        </q-card-actions>
      </q-form>
    </q-card-section>
  </q-card>
</q-dialog>


  <!-- Delete Product Dialog -->
  <q-dialog v-model="showDeleteDialog">
    <q-card>
      <q-card-section class="row items-center">
        <q-avatar icon="warning" color="negative" text-color="white" />
        <span class="q-ml-sm">Are you sure you want to delete this product?</span>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Cancel" color="primary" v-close-popup />
        <q-btn flat label="Delete" color="negative" @click="confirmDelete" />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <SaleDialog
  v-model="showSaleDialog"
  :product="selectedProduct"
  @saleRecorded="fetchProducts"
/>


</template>

<style>
.q-toolbar-title {
  font-size: 18px;
}
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 8px;
}
.q-dialog-card {
  min-width: 400px;
  max-width: 500px;
  border-radius: 10px;
}
.q-card {
  border-radius: 12px; 
}
.sales-card {
  transition: 0.3s;
}

.sales-card:hover {
  transform: scale(1.05);
}
.q-btn {
  transition: all 0.2s ease-in-out;
}

.q-btn:hover {
  transform: scale(1.05);
}

.custom-table {
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #ddd; 
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); /* Subtle shadow */
}

</style>
