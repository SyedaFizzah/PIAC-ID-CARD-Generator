export function filterInterns(interns, filters) {
    return interns.filter((intern) => {

        const matchesSearch =
            !filters.search ||
            [
                intern.unique_id,
                intern.name,
                intern.department,
                intern.university,
                intern.discipline,
                intern.cnic,
            ]
                .filter(Boolean)
                .some(field =>
                    field.toLowerCase().includes(filters.search.toLowerCase())
                );

        const matchesGender =
            !filters.gender || intern.gender === filters.gender;

        const matchesDepartment =
            !filters.department || intern.department === filters.department;

        return matchesSearch && matchesGender && matchesDepartment;
    });
}
