function updateOrderPayment(order_id,response){
    var data = {order_id:order_id,gateway_order_id:response.razorpay_order_id,gateway_payment_id:response.razorpay_payment_id,gateway_signature:response.razorpay_signature};
    $.ajax({
        url: "{{url('api:updateorderpaymentapi')}}",
        headers: { 
            'Accept': 'application/json',
            'Content-Type': 'application/json' 
        },
        type: 'POST',
        data:JSON.stringify(data),
        success: function (data) {
            window.location.href = "{{url('shop:orderplaced')}}";
        },
        error: function(data){
            enableBtn();
            $('#checkoutbtn').hide();
            $('#retrypaymentbtn').show();
            // console.log($.parseJSON(data));
            try{
                // alert($.parseJSON(data));
                alert(data.responseJSON.message);
            }
            catch(e){
                alert("Internal Server Error");
            }
          },
        cache: false,
        contentType: false,
        processData: false
    });

}