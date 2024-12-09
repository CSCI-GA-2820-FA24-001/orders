const API_BASE_URL = "/api"

function fetchOrders() {
    $.ajax({
      url: `${API_BASE_URL}/orders`,
      method: "GET",
      success: function (orders) {
        orders.forEach((order) => renderOrder(order));
      },
      error: function (xhr, status, error) {
        console.error("Failed to fetch orders:", error);
      },
    });
  }
  
  // Call this function on page load
  $(document).ready(function () {
    fetchOrders();
  });

  function renderOrder(order) {
    const container = $("#ordersContainer");
    
    const orderDiv = $("<div>").addClass("order");
  
    const orderTitle = $("<div>").text(`Order ${order.id}`);
    orderDiv.append(orderTitle);
  
    const orderInfoBtn = $("<button>")
      .addClass("order-info-btn")
      .html(`
        <div>Customer: ${order.customer_name}</div>
        <div>Status: ${order.status}</div>
      `)
      .click(() =>
        openEditOrderModal(orderDiv, order)
      );
    orderDiv.append(orderInfoBtn);
  
    const itemListHeader = $("<div>")
      .addClass("item-list-header")
      .html(`
        <span>Item</span>
        <span>Quantity</span>
        <span>Price</span>
      `);
    orderDiv.append(itemListHeader);
  
    const itemList = $("<div>").addClass("item-list");
    order.items.forEach((item) => renderItem(itemList, item, order.id));
    orderDiv.append(itemList);
  
    const addItemBtn = $("<button>")
      .addClass("add-item-btn")
      .text("Add Item")
      .click(() => addItem(itemList, order.id));
    orderDiv.append(addItemBtn);
  
    const deleteBtn = $("<button>")
      .addClass("delete-order-btn")
      .text("Delete Order")
      .click(() => deleteOrder(order.id, orderDiv));
    orderDiv.append(deleteBtn);
  
    // Insert the new order tab right before the "New Order" button
    const newOrderBtn = $(".new-order");
    orderDiv.insertBefore(newOrderBtn); 
  }
  

function addOrder() {
    const newOrder = {
      customer_name: `VOID`, // Use timestamp to generate unique name
      status: "CREATED",
      items: [],
    };
  
    $.ajax({
      url: `${API_BASE_URL}/orders`,
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify(newOrder),
      success: function (order) {
        renderOrder(order);
      },
      error: function (xhr, status, error) {
        console.error("Failed to add order:", error);
      },
    });
  }
  
  function deleteOrder(orderId, orderDiv) {
    $.ajax({
      url: `${API_BASE_URL}/orders/${orderId}`,
      method: "DELETE",
      success: function () {
        orderDiv.remove();
      },
      error: function (xhr, status, error) {
        console.error("Failed to delete order:", error);
      },
    });
  }
  
  function addItem(itemList, orderId) {
    const newItem = {
      product_name: `VOID`,
      quantity: 0,
      price: 0,
    };
  
    $.ajax({
      url: `${API_BASE_URL}/orders/${orderId}/items`,
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify(newItem),
      success: function (item) {
        renderItem(itemList, item, orderId);
      },
      error: function (xhr, status, error) {
        console.error("Failed to add item:", error);
      },
    });
  }
  
  function renderItem(itemList, item, orderId) {
    const itemDiv = $("<div>")
      .addClass("item")
      .html(`
        <span>${item.product_name}</span>
        <span>${item.quantity}</span>
        <span>$${parseFloat(item.price).toFixed(2)}</span>
      `)
      .click(() => openEditItemModal(itemDiv, item, orderId));
  
    itemList.append(itemDiv);
  }
  
  
function openEditOrderModal(orderDiv, order) {
    const modal = $('#orderModal');
    modal.css("display", "flex");
  
    $("#customerInput").val(order.customer_name);
    $("#statusInput").val(order.status);
  
    $("#save-order-btn").off("click").on("click", function () {
      const newCustomer = $("#customerInput").val();
      const newStatus = $("#statusInput").val();
  
      $.ajax({
        url: `${API_BASE_URL}/orders/${order.id}`,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify({
          customer_name: newCustomer,
          status: newStatus,
        }),
        success: function (updatedOrder) {
          $(orderDiv).find('.order-info-btn').html(`
            <div>Customer: ${updatedOrder.customer_name}</div>
            <div>Status: ${updatedOrder.status}</div>
          `);
          order.customer_name = updatedOrder.customer_name;
        order.status = updatedOrder.status;
          modal.hide(); // 
        },
        
        error: function (xhr, status, error) {
          console.error('Failed to update order info:', error);
        },
      });
    });
  
    $("#cancel-order-btn").off("click").on("click", function () {
      modal.hide(); // 
    });
  }
  
  
  
  // Close the edit item modal
function closeOrderModal() {
    const modal = document.querySelector('#orderModal');
    modal.style.display = 'none';
}
  
function openEditItemModal(itemDiv, item, orderId) {
    const modal = $("#itemModal");
    modal.css("display", "flex");
  
    $("#itemNameInput").val(item.product_name);
    $("#itemQuantityInput").val(item.quantity);
    $("#itemPriceInput").val(item.price);
  
    $("#save-item-btn").off("click").on("click", function () {
      const updatedItem = {
        product_name: $("#itemNameInput").val(),
        quantity: parseInt($("#itemQuantityInput").val(), 10),
        price: parseFloat($("#itemPriceInput").val()),
      };
  
      $.ajax({
        url: `${API_BASE_URL}/orders/${orderId}/items/${item.id}`,
        method: "PUT",
        contentType: "application/json",
        data: JSON.stringify(updatedItem),
        success: function (updated) {
            item.product_name = updated.product_name;
            item.quantity = updated.quantity;
            item.price = updated.price;
          itemDiv.html(`
            <span>${updated.product_name}</span>
            <span>${updated.quantity}</span>
            <span>$${parseFloat(updated.price).toFixed(2)}</span>
          `);
          modal.hide();
        },
        error: function (xhr, status, error) {
          console.error("Failed to update item:", error);
        },
      });
    });
  
    $("#delete-item-btn").off("click").on("click", function () {
      $.ajax({
        url: `${API_BASE_URL}/orders/${orderId}/items/${item.id}`,
        method: "DELETE",
        success: function () {
          itemDiv.remove();

          modal.hide();
        },
        error: function (xhr, status, error) {
          console.error("Failed to delete item:", error);
        },
      });
    });
  
    $("#cancel-item-btn").off("click").on("click", function () {
      modal.hide();
    });
  }
  

// Close the edit item modal
function closeItemModal() {
  const modal = $('#itemModal');
  modal.style.display = 'none';
}


function filterOrders() {
    const customerName = $("#filter-customer-name").val().trim();
    const orderStatus = $("#filter-order-status").val().trim();
    const productName = $("#filter-product-name").val().trim();

    const queryParams = new URLSearchParams();
    if (customerName) {
        queryParams.append("name", customerName);
    }
    if (orderStatus) {
        queryParams.append("order_status", orderStatus);
    }
    if (productName) {
        queryParams.append("product_name", productName);
    }

    $.ajax({
        url: `${API_BASE_URL}/orders?${queryParams.toString()}`,
        method: "GET",
        success: function (orders) {
            $("#ordersContainer").html(`
                <button class="new-order" onclick="addOrder()" id="new-order-btn">New Order</button>
            `);

            orders.forEach((order) => renderOrder(order));
        },
        error: function (xhr, status, error) {
            console.error("Failed to filter orders:", error);
        },
    });
}