from django.http import HttpResponse
from django.shortcuts import render
from .models import product, Contact,Orders,OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt

from PAYTM import checksum
MERCHANT_KEY = 'kbzk1DsbJiv_O3p5'


def index(request):
  # products=product.objects.all()
  # print(products)
  # n=len(products)
  # nslides=n//4+ceil((n/4)-(n//4))
  # params={'no_of_slides':nslides,'range':range(1,nslides),'product':products}
  # allprods=[[products,range(1,nslides),nslides],
  #          [products,range(1,nslides),nslides] ]
  allprods=[]
  catprods=product.objects.values('category','id')
  cats={item['category'] for item in catprods}
  for cat in cats:
    prod=product.objects.filter(category=cat)
    n=len(prod)
    nslides=n//4+ceil((n/4)-(n//4))
    allprods.append([prod,range(1,nslides),nslides])
  
  params={'allprods':allprods}

  return render(request, 'shop/index.html',params)


def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False
   
def search(request):
    query= request.GET.get('search')
    allProds = []
    catprods = product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = product.objects.filter(category=cat)
        prod=[item for item in prodtemp if searchMatch(query, item)]
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod)!= 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds,'msg':""}
    if len(allProds)==0 or len(query)<4:
        params={'msg':"Please make sure to enter relevant search query"}
    return render(request, 'shop/search.html', params)

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    thank=False
    if request.method=="POST":
        
        name=request.POST.get('name', '')
        email=request.POST.get('email', '')
        phone=request.POST.get('phone', '')
        desc=request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank=True
    return render(request, "shop/contact.html",{'thank':thank})

def tracker(request):
  if request.method=="POST":
    orderId=request.POST.get('orderId','')
    email=request.POST.get('email','')
    try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
    except Exception as e:
            return HttpResponse('{"status":"error"}')
          

  return render(request,'shop/tracker.html')



    

    


    # query= request.GET.get('search')
    # allProds = []
    # catprods = product.objects.values('category', 'id')
    # cats = {item['category'] for item in catprods}
    # for cat in cats:
    #     prodtemp = product.objects.filter(category=cat)
    #     prod=[item for item in prodtemp if searchMatch(query, item)]
    #     n = len(prod)
    #     nSlides = n // 4 + ceil((n / 4) - (n // 4))
    #     if len(prod)!= 0:
    #         allProds.append([prod, range(1, nSlides), nSlides])
    # params = {'allProds': allProds, "msg":""}
    # if len(allProds)==0 or len(query)<4:
    #     params={'msg':"Please make sure to enter relevant search query"}
    # return render(request, 'shop/index.html', params)



def productview(request,myid):
  #fetching the products using id
   Product=product.objects.filter(id=myid)
  

   return render(request,'shop/productview.html',{'Product':Product[0]})

def checkout(request):
  if request.method=="POST":
        items_json=request.POST.get('itemsJson',"")
        name=request.POST.get('name', '')
        amount=request.POST.get('amount', '')
        email=request.POST.get('email', '')
        address=request.POST.get('address1', '')+" "+request.POST.get('address2','')
        city=request.POST.get('city', '')
        state=request.POST.get('state', '')
        zip_code=request.POST.get('zip_code', '')
        phone=request.POST.get('phone', '')
        order = Orders(items_json= items_json ,name=name,amount=amount, email=email, address=address,city=city,state=state,zip_code=zip_code,phone=phone)
        order.save()
        update=OrderUpdate(order_id=order.order_id,update_desc="The Order Has Been Placed")
        update.save()
        thank=True
        id=order.order_id
        #return render(request, 'shop/checkout.html', {'thank':thank, 'id':id})
        #request paytm to transfer the amount to our account ater payment by user

        param_dict={
          #for payment required 
          #use merchant id and key are used in production which is provided by paytm and donot share key and id to anyone
            'MID': 'WorldP64425807474247',
            'ORDER_ID': str(order.order_id),
            'TXN_AMOUNT': str(amount),
            'CUST_ID': 'email',
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',

        }
        param_dict['CHECKSUMHASH']=checksum.generate_checksum(param_dict,MERCHANT_KEY)
        return  render(request, 'shop/paytm.html', {'param_dict': param_dict})
        
  return render(request,'shop/checkout.html')

@csrf_exempt

def handlerequest(request):
    # paytm will send post request here
    #return HttpResponse('done')
    
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
          Checksum = form[i]

    verify = checksum.verify_checksum(response_dict, MERCHANT_KEY, Checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})