function deleteTeacher(teacherId) {
    const options = {
        method: 'DELETE',
        headers: {'Content-Type': 'application/json'},
    };
    fetch(`/delete_teacher/${teacherId}`, options)
        .then(response => {
            if (response.status === 200) {
                location.reload();
            } else {
                alert('Error deleting teacher, please try again later');
            }
        })
        .catch(error => console.error('An error occurred:', error));
}
