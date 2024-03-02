function deleteCourse(courseId) {
    const options = {
        method: 'DELETE',
        headers: {'Content-Type': 'application/json'},
    };
    fetch(`delete_course/${courseId}`, options)
        .then(response => {
            if (response.status === 200) {
                location.reload();
            } else {
                alert('Ошибка удаления, пожалуйста, попробуйте заново позже');
            }
        })
        .catch(error => console.error('Произошла ошибка:', error));
}