const BASE_URL = "/api"
$(function () {
    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#order_id").val(res.id);
        $("#order_customer_name").val(res.customer_name);
        $("#order_status").val(res.status);

        // Handle items array - taking first item for now
        if (res.items && res.items.length > 0) {
            let item = res.items[0];
            $("#order_product_name").val(item.product_name);
            $("#order_quantity").val(item.quantity);
            $("#order_price").val(item.price);
        }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#order_customer_name").val("");
        $("#order_status").val("");
        $("#order_product_name").val("");
        $("#order_quantity").val("");
        $("#order_price").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create an Order
    // ****************************************

    $("#create-btn").click(function () {
        let customer_name = $("#order_customer_name").val();
        let status = $("#order_status").val();

        let data = {
            "customer_name": customer_name,
            "status": status,
            "items": {}
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: BASE_URL+"/orders",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Update an Order
    // ****************************************

    $("#update-btn").click(function () {
        let order_id = $("#order_id").val();
        let customer_name = $("#order_customer_name").val();
        let status = $("#order_status").val();
        let product_name = $("#order_product_name").val();
        let quantity = $("#order_quantity").val();
        let price = $("#order_price").val();

        let data = {
            "customer_name": customer_name,
            "status": status,
            "items": [{
                "product_name": product_name,
                "quantity": parseInt(quantity),
                "price": parseFloat(price)
            }]
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: BASE_URL+`/orders/${order_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Retrieve an Order
    // ****************************************

    $("#retrieve-btn").click(function () {
        let order_id = $("#order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: BASE_URL+`/orders/${order_id}`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Delete an Order
    // ****************************************

    $("#delete-btn").click(function () {
        let order_id = $("#order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: BASE_URL+`/orders/${order_id}`,
            contentType: "application/json",
            data: '',
        });

        ajax.done(function(res){
            clear_form_data()
            flash_message("Order has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });
    

    // ****************************************
    // Cancel an Order
    // ****************************************

    $("#cancel-btn").click(function () {
        let order_id = $("#order_id").val();
        let customer_name = $("#order_customer_name").val();
        let status = $("#order_status").val();
        let product_name = $("#order_product_name").val();
        let quantity = $("#order_quantity").val();
        let price = $("#order_price").val();

        let data = {
            "customer_name": customer_name,
            "status": status,
            "items": [{
                "product_name": product_name,
                "quantity": parseInt(quantity),
                "price": parseFloat(price)
            }]
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: BASE_URL+`/orders/${order_id}/cancel`,
            contentType: "application/json",
            data: JSON.stringify(data)
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#order_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for Orders
    // ****************************************

    $("#search-btn").click(function () {
        let customer_name = $("#order_customer_name").val();
        let status = $("#order_status").val();
        let product_name = $("#order_product_name").val();

        let queryString = "";
        if (customer_name) {
            queryString += 'name=' + customer_name;
        }
        if (status) {
            if (queryString.length > 0) {
                queryString += '&';
            }
            queryString += 'order_status=' + status;
        }
        if (product_name) {
            if (queryString.length > 0) {
                queryString += '&';
            }
            queryString += 'product_name=' + product_name;
        }

        $("#flash_message").empty();
        flash_message("searching.. ")
        
        let ajax = $.ajax({
            type: "GET",
            url: BASE_URL+`/orders${queryString ? '?' + queryString : ''}`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">';
            table += '<thead><tr>';
            table += '<th class="col-md-2">ID</th>';
            table += '<th class="col-md-2">Customer Name</th>';
            table += '<th class="col-md-2">Status</th>';
            table += '<th class="col-md-2">Product Name</th>';
            table += '<th class="col-md-2">Quantity</th>';
            table += '<th class="col-md-2">Price</th>';
            table += '</tr></thead><tbody>';
            
            let firstOrder = "";
            for(let i = 0; i < res.length; i++) {
                let order = res[i];
                let item = order.items[0] || {}; // Get first item or empty object if no items
                table += `<tr id="row_${i}">`;
                table += `<td>${order.id}</td>`;
                table += `<td>${order.customer_name}</td>`;
                table += `<td>${order.status}</td>`;
                table += `<td>${item.product_name || ''}</td>`;
                table += `<td>${item.quantity || ''}</td>`;
                table += `<td>${item.price || ''}</td>`;
                table += '</tr>';
                if (i == 0) {
                    firstOrder = order;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstOrder != "") {
                update_form_data(firstOrder)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************************
    //  U T I L I T Y   F U N C T I O N S  F O R  I T E M S
    // ****************************************************

    // Updates the form with data from the response
    function update_item_form_data(res) {
            $("#item_id").val(res.id);
            $("#item_product_name").val(res.product_name);
            $("#item_quantity").val(res.quantity);
            $("#item_price").val(res.price);
    }

    // clears the item form data
    function clear_item_form_data() {
        $("#order_id_item").val("");
        $("#item_id").val("");
        $("#item_product_name").val("");
        $("#item_quantity").val("");
        $("#item_price").val("");
    }

    // Updates the flash message item area
    function flash_item_message(message) {
        $("#flash_message_item").empty();
        $("#flash_message_item").append(message);
    }

    // ****************************************
    // Create an item in Order
    // ****************************************

    $("#create-item-btn").click(function () {
        let order_id = $("#order_id_item").val();
        let product_name = $("#item_product_name").val();
        let quantity = $("#item_quantity").val();
        let price = $("#item_price").val();

        let data = {
            "product_name": product_name,
            "quantity": parseInt(quantity),
            "price": parseFloat(price)
        };

        $("#flash_message_item").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: BASE_URL+`/orders/${order_id}/items`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_item_form_data(res)
            flash_item_message("Success")
        });

        ajax.fail(function(res){
            flash_item_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Update an item in Order
    // ****************************************

    $("#update-item-btn").click(function () {
        let order_id = $("#order_id_item").val();
        let item_id = $("#item_id").val();
        let product_name = $("#item_product_name").val();
        let quantity = $("#item_quantity").val();
        let price = $("#item_price").val();

        let data = {
            "product_name": product_name,
            "quantity": parseInt(quantity),
            "price": parseFloat(price)
        };

        $("#flash_message_item").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: BASE_URL+`/orders/${order_id}/items/${item_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        });

        ajax.done(function(res){
            update_item_form_data(res)
            flash_item_message("Success")
        });

        ajax.fail(function(res){
            flash_item_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Retrieve all items in Order
    // ****************************************

    $("#retrieve-item-btn").click(function () {
        let order_id = $("#order_id_item").val();
        let item_id = $("#item_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: BASE_URL+`/orders/${order_id}/items/${item_id}`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            update_item_form_data(res)
            flash_item_message("Success")
        });

        ajax.fail(function(res){
            clear_item_form_data()
            flash_item_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Delete an item in Order
    // ****************************************

    $("#delete-item-btn").click(function () {
        let order_id = $("#order_id_item").val();
        let item_id = $("#item_id").val();

        $("#flash_message_item").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: BASE_URL+`/orders/${order_id}/items/${item_id}`,
            contentType: "application/json",
            data: '',
        });

        ajax.done(function(res){
            clear_item_form_data()
            flash_item_message("Item has been Deleted!")
        });

        ajax.fail(function(res){
            flash_item_message("Server error!")
        });
    });
    

    // ****************************************
    // Clear the item form
    // ****************************************

    $("#clear-item-btn").click(function () {
        $("#order_id_item").val("");
        $("#item_id").val("");
        $("#item_product_name").val("");
        $("#item_quantity").val("");
        $("#item_price").val("");
        $("#flash_message_item").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for items in an Order
    // ****************************************

    $("#search-item-btn").click(function () {
        let order_id = $("#order_id_item").val();
        
        $("#flash_message_item").empty();

        let ajax = $.ajax({
            type: "GET",
            url: BASE_URL+`/orders/${order_id}/items`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            $("#search_results_item").empty();
            let table = '<table class="table table-striped" cellpadding="10">';
            table += '<thead><tr>';
            table += '<th class="col-md-2">Item ID</th>';
            table += '<th class="col-md-2">Product Name</th>';
            table += '<th class="col-md-2">Quantity</th>';
            table += '<th class="col-md-2">Price</th>';
            table += '</tr></thead><tbody>';
            
            let firstItem = "";
            flash_item_message("len="+res.length)
            for(let i = 0; i < res.length; i++) {
                let item = res[i];
                table += `<tr id="row_${i}">`;
                table += `<td>${item.id}</td>`;
                table += `<td>${item.product_name}</td>`;
                table += `<td>${item.quantity}</td>`;
                table += `<td>${item.price}</td>`;
                table += '</tr>';
                if (i == 0) {
                    firstItem = item;
                }
            }
            table += '</tbody></table>';
            $("#search_results_item").append(table);

            // copy the first result to the form
            if (firstItem != "") {
                update_item_form_data(firstItem)
            }

            flash_item_message("Success")
        });

        ajax.fail(function(res){
            flash_item_message(res.responseJSON.message)
        });
    });

});