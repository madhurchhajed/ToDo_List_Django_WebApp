from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, authenticate, logout
from .forms import TodoForm
from .models import Todo
from django.utils import timezone


# Create your views here.

def home(request):
    return render(request, 'todo/home.html')


def signup(request):
    if request.method == 'GET':
        return render(request, 'todo/signup.html',
                      {'form': UserCreationForm})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    request.POST['username'],
                    password=request.POST['password2'])
                user.save()
                login(request, user)
                return redirect('home')

            except IntegrityError:
                return render(request, 'todo/signup.html',
                              {'form': UserCreationForm,
                               'error': "username is already taken, pick new username"})


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html',
                      {'form': AuthenticationForm}
                      )
    else:
        user = authenticate(request, username=request.POST['username'],
                            password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html',
                          {'error': 'username and password did not match'}
                          )
        else:
            login(request, user)
            return redirect('current_todo')


@login_required
def current_todo(request):
    todos = Todo.objects.filter(user=request.user, completed_date__isnull=True)
    return render(request, 'todo/current_todo.html', {'todos': todos})


@login_required
def view_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    form = TodoForm(instance=todo)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/view_todo.html', {'todo': todo,
                                                       'form': form
                                                       })
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('current_todo')
        except ValueError:
            return render(request, 'todo/view_todo.html',
                          {'todo': todo,
                           'form': form,
                           'error': 'Bad Value passed'
                           })


def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


def create_todo(request):
    if request.method == "GET":
        return render(request, 'todo/create_todo.html',
                      {'form': TodoForm()}
                      )
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('current_todo')
        except ValueError:
            return render(request, 'todo/create_todo.html',
                          {'form': TodoForm(),
                           'error': "Value Error: Bad Data"}
                          )


@login_required
def complete_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.completed_date = timezone.now()
        todo.save()
        return redirect('current_todo')


@login_required
def completed_todo(request):
    todos = Todo.objects.filter(user=request.user,
                                completed_date__isnull=False).order_by('-completed_date')
    return render(request, 'todo/completed_todo.html', {'todos': todos})


def delete_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.delete()
        return redirect('current_todo')
