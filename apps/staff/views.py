from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import StaffProfile, Department
from .forms import StaffProfileForm, DepartmentForm


@login_required
def staff_list(request):
    """List all staff members"""
    staff_members = StaffProfile.objects.select_related('user', 'department').filter(is_active=True)
    return render(request, 'staff/staff_list.html', {'staff_members': staff_members})


@login_required
def staff_create(request):
    """Create a new staff member"""
    if request.method == 'POST':
        form = StaffProfileForm(request.POST)
        if form.is_valid():
            staff = form.save()
            messages.success(request, f'Staff member {staff.user.get_full_name()} created successfully.')
            return redirect('staff_list')
    else:
        form = StaffProfileForm()
    
    return render(request, 'staff/staff_form.html', {'form': form, 'title': 'Add Staff Member'})


@login_required
def staff_detail(request, pk):
    """View staff member details"""
    staff = get_object_or_404(StaffProfile, pk=pk)
    return render(request, 'staff/staff_detail.html', {'staff': staff})


@login_required
def staff_edit(request, pk):
    """Edit staff member"""
    staff = get_object_or_404(StaffProfile, pk=pk)
    if request.method == 'POST':
        form = StaffProfileForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, f'Staff member {staff.user.get_full_name()} updated successfully.')
            return redirect('staff_list')
    else:
        form = StaffProfileForm(instance=staff)
    
    return render(request, 'staff/staff_form.html', {'form': form, 'title': 'Edit Staff Member'})


@login_required
def staff_delete(request, pk):
    """Delete staff member"""
    staff = get_object_or_404(StaffProfile, pk=pk)
    if request.method == 'POST':
        name = staff.user.get_full_name()
        staff.delete()
        messages.success(request, f'Staff member {name} deleted successfully.')
        return redirect('staff_list')
    
    return render(request, 'staff/staff_confirm_delete.html', {'staff': staff})


# Department views
@login_required
def department_list(request):
    """List all departments"""
    departments = Department.objects.select_related('manager').filter(is_active=True)
    return render(request, 'staff/department_list.html', {'departments': departments})


@login_required
def department_create(request):
    """Create a new department"""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            messages.success(request, f'Department {department.name} created successfully.')
            return redirect('department_list')
    else:
        form = DepartmentForm()
    
    return render(request, 'staff/department_form.html', {'form': form, 'title': 'Add Department'})


@login_required
def department_detail(request, pk):
    """View department details"""
    department = get_object_or_404(Department, pk=pk)
    return render(request, 'staff/department_detail.html', {'department': department})


@login_required
def department_edit(request, pk):
    """Edit department"""
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, f'Department {department.name} updated successfully.')
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    
    return render(request, 'staff/department_form.html', {'form': form, 'title': 'Edit Department'})


@login_required
def department_delete(request, pk):
    """Delete department"""
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        name = department.name
        department.delete()
        messages.success(request, f'Department {name} deleted successfully.')
        return redirect('department_list')
    
    return render(request, 'staff/department_confirm_delete.html', {'department': department})
