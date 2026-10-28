function EventTable({ events }) {
    return (
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Time</th>
                    <th>Image</th>
                </tr>
            </thead>

            <tbody>
                {events.map((event) => (
                    <tr key={event.id}>
                        <td>{event.id}</td>
                        <td>{event.timestamp}</td>
                        <td>
                            <img
                                src={event.image_path}
                                width="120"
                            />
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
}

export default EventTable;