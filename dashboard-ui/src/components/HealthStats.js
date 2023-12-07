import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

    const getTimeStamp = () => {
        const timestamp = Date.now(); // Get the current timestamp in milliseconds
        const date = new Date(timestamp); // Convert timestamp to a Date object
        const formattedDate = date.toLocaleString(); // Get a human-readable date string
        return formattedDate;
    };

	const getStats = () => {
	
        fetch(`http://acit3855.westus.cloudapp.azure.com/health/health`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Health Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<td>Reciever: {stats['receiver']}</td>
						</tr>
						<tr>
                            <td>Storage: {stats['storage']}</td>
						</tr>
						<tr>
                            <td>Processing: {stats['processing']}</td>
						</tr>
                        <tr>
                            <td>Audit: {stats['audit']}</td>
						</tr>
                        <tr>
                            <td>Last Updated: {stats['last_updated']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {getTimeStamp()}</h3>

            </div>
        )
    }
}
