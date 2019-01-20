from django.shortcuts import render
from django.shortcuts import redirect
from financial.models import *

import datetime

from django.http import HttpResponse
import csv
import hashlib
# Create your views here.


def home(request):
    return render(request, "home.html", {"name": request.session.get("name")})


def view(request, *args):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    username = request.session["name"]
    if request.method == 'POST':
        if 'Category' in request.POST:
            categoryName = request.POST["Category"]
            balances = Balance.objects.filter(
                categoryName=categoryName, writer=username)
        else:
            balances = Balance.objects.filter(writer=username)
    else:
        balances = Balance.objects.filter(writer=username)
    incomes = []
    expences = []
    categories = Category.objects.filter(writer=username)
    incomeCategories = Category.objects.filter(balance=True, writer=username)
    expenseCategories = Category.objects.filter(balance=False, writer=username)
    categories = categories.values(
        'categoryName').order_by('categoryName').distinct()
    sumIncomes = 0
    sumExpences = 0
    for balance in balances:
        if balance.isIncome:
            incomes += [balance]
            sumIncomes += balance.amount
        else:
            expences += [balance]
            sumExpences += balance.amount
    gain = sumIncomes - sumExpences
    # グラフの用意
    if len(incomes) > 0:
        label = []
        amount = []
        for income in incomes:
            if not income.categoryName in label:
                label += [income.categoryName]
                amount += [income.amount]
            else:
                index = label.index(income.categoryName)
                amount[index] += income.amount
        fig = plt.figure(1, figsize=(4, 4))
        ax = fig.add_subplot(111)
        ax.axis("equal")
        ax.pie(amount,  # データ
               startangle=90,  # 円グラフ開始軸を指定
               labels=label,  # ラベル
               autopct="%1.1f%%",  # パーセント表示
               # colors=colors,  # 色指定
               counterclock=False,  # 逆時計回り
               )
        plt.savefig('figure.png')
    if len(args) >= 2:  # 　入力内容によるエラー表示
        return render(request, "view.html",
                      {args[0]: args[1], "name": request.session.get("name"), "balances": balances, "gain": gain,
                       "incomeCategories": incomeCategories, "expenseCategories": expenseCategories, "Category": categories})
    else:
        return render(request, "view.html",
                      {"name": request.session.get("name"), "balances": balances, "gain": gain, "incomeCategories": incomeCategories, "expenseCategories": expenseCategories, "Category": categories})


def income(request):
    inputIncomeStr = request.POST["income"]
    description = request.POST["incomeDescription"]
    if inputIncomeStr.isdecimal() and description != "":  # 入力が数字の時
        inputIncome = int(inputIncomeStr)
        categoryName = request.POST["incomeCategory"]
        username = request.session["name"]
        income = Balance(description=description, amount=inputIncome, isIncome=True, date=datetime.date.today(),
                         categoryName=categoryName, writer=username)
        income.save()
        return view(request)
    else:  # 入力が数字でない時のエラー
        if not inputIncomeStr.isdecimal():
            return view(request, "incomeError", "notDecimalError")
        else:
            return view(request, "incomeError", "contentBlankError")


def expence(request):
    inputExpenceStr = request.POST["expence"]
    description = request.POST["expenceDescription"]
    if inputExpenceStr.isdecimal() and description != "":
        inputExpence = int(inputExpenceStr)
        categoryName = request.POST["expenseCategory"]
        username = request.session["name"]
        expence = Balance(description=description, amount=inputExpence, isIncome=False, date=datetime.date.today(),
                          categoryName=categoryName, writer=username)
        expence.save()
        return view(request)
    else:  # 入力エラーの時
        if not inputExpenceStr.isdecimal():
            return view(request, "expenseError", "notDecimalError")
        else:
            return view(request, "expenseError", "contentBlankError")

def signin(request):
    return render(request, "signin.html", {"error": "none"})


def signup(request):
    return render(request, "signup.html", {"error": "none"})


def signinconfirm(request):
    name = request.POST["name"]
    password = request.POST["password"]
    if len(User.objects.filter(name=name)) != 0:
        user = User.objects.filter(name=name)[0]
        for val in range(0,1000):
            password = hashlib.sha256((str(user.id)+password).encode('utf-8')).hexdigest()
        if User.objects.filter(name=name)[0].password == password:
            request.session["name"] = name
            return view(request)
        else:
            return render(request, "signin.html", {"error": "password"})
    else:
        return render(request, "signin.html", {"error": "name"})


def signupconfirm(request):
    name = request.POST["name"]
    password = request.POST["password"]
    if len(User.objects.filter(name=name)) == 0:
        user = User(name=name, password="")
        user.save()
        for val in range(0,1000):
            password = hashlib.sha256((str(user.id)+password).encode('utf-8')).hexdigest()
        user.password = password
        user.save()
        return render(request, "signupconfirm.html")
    else:
        return render(request, "signup.html", {"error": "name"})


def signout(request):
    request.session.clear()
    return render(request, "home.html", {"name": request.session.get("name")})


def category(request):  # カテゴリー登録関数
    inputCategory = request.POST["registrationCategory"]
    categoryType = request.POST["categoryType"]
    IncomeCategory = Category.objects.filter(balance=True)
    ExpenseCategory = Category.objects.filter(balance=False)
    username = request.session["name"]
    if inputCategory == "":
        return view(request, "categorySubscribeError", "blank")
    if categoryType == "income":
        if len(Category.objects.filter(categoryName=inputCategory, balance=True, writer=username)) == 0:
            newcategory = Category(
                categoryName=inputCategory, balance=True, writer=username)
            newcategory.save()
        else:
            return view(request, "categorySubscribeError", "duplication")
    else:
        if len(Category.objects.filter(categoryName=inputCategory, balance=False, writer=username)) == 0:
            newcategory = Category(
                categoryName=inputCategory, balance=False, writer=username)
            newcategory.save()
        else:
            return view(request, "categorySubscribeError", "duplication")
    return render(request, "category.html")

def export(request): #csvファイルをエクスポート
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data.csv"'
    writer = csv.writer(response)
    balances = Balance.objects.filter(writer=request.session.get("name")) #あとで日付順にソートすべき
    for balance in balances: #今は収支、内容、カテゴリーのみ。後で追加
        if(balance.isIncome):
            writer.writerow([balance.amount, balance.description, balance.categoryName])
        else:
            writer.writerow([-balance.amount, balance.description, balance.categoryName])
    return response
