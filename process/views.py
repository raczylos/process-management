from datetime import datetime
import psutil
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.exceptions import PermissionDenied
from .models import Snapshot
import ast
from django.utils import timezone

@login_required
def home(request):
    return render(request, 'process/home.html')


@login_required
def process_list(request):
    user = request.user

    if not user.is_superuser:
        raise PermissionDenied("You do not have permission to view this data!")

    pid_filter = request.GET.get('pid', '').strip()
    name_filter = request.GET.get('name', '').strip().lower()
    status_filter = request.GET.get('status', '').strip().lower()

    system_processes = []
    for proc in psutil.process_iter(["pid", "name", "status", "create_time", "memory_info"]):
        try:
            if proc.info["pid"] == 0:
                continue

            process_info = {
                "pid": proc.info["pid"],
                "name": proc.info["name"],
                "status": proc.info["status"].lower(),
                "start_time": datetime.fromtimestamp(proc.info["create_time"]).isoformat(),
                "memory_usage": proc.info["memory_info"].rss // (1024 * 1024),
                "cpu_usage": f"{proc.cpu_percent(interval=None)}%"
            }

            if pid_filter and str(proc.info["pid"]) != pid_filter:
                continue
            if name_filter and name_filter not in proc.info["name"].lower():
                continue
            if status_filter and proc.info["status"].lower() != status_filter:
                continue

            system_processes.append(process_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    sort_key = request.GET.get('sort', 'memory_usage')
    sort_order = request.GET.get('order', 'desc')
    reverse_sort = True if sort_order == 'desc' else False

    system_processes.sort(key=lambda x: x.get(sort_key, 0), reverse=reverse_sort)

    current_time = timezone.now()

    return render(request, 'process/process_list.html', {
        'processes': system_processes,
        'current_time': current_time,
        'sort_key': sort_key,
        'sort_order': sort_order,
        'pid_filter': pid_filter,
        'name_filter': name_filter,
        'status_filter': status_filter,
    })

@login_required
def kill_process(request, pid):
    user = request.user

    if not user.is_superuser:
        raise PermissionDenied("You do not have permission to kill processes!")

    try:
        proc = psutil.Process(pid)
        proc.kill()
        return redirect('home')
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
def save_snapshot(request):
    user = request.user

    if not user.is_superuser:
        raise PermissionDenied("You do not have permission to save a snapshot!")

    if request.method == 'POST':

        process_data_string = request.POST.get('process_data', None)

        if not process_data_string:
            return redirect('home')
        process_data = ast.literal_eval(process_data_string)

        snapshot = Snapshot.objects.create(
            author=user,
            process_data=process_data
        )

        return redirect('snapshot_list')

    return redirect('home')


@login_required
def snapshot_list(request):
    user = request.user

    if not user.is_superuser:
        raise PermissionDenied("You do not have permission to view snapshots!")

    snapshots = Snapshot.objects.all().order_by('-timestamp')

    return render(request, 'process/snapshot_list.html', {'snapshots': snapshots})


@login_required
def snapshot_detail(request, snapshot_id):
    user = request.user

    if not user.is_superuser:
        raise PermissionDenied("You do not have permission to view this snapshot!")

    snapshot = get_object_or_404(Snapshot, id=snapshot_id)

    return render(request, 'process/snapshot_detail.html', {'snapshot': snapshot})
