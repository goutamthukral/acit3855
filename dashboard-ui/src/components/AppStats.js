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
	
        fetch(`http://acit3855.westus.cloudapp.azure.com:8100/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
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
							<th>Temperature</th>
							<th>Weather</th>
						</tr>
						<tr>
							<td>Number of Temperature Readings: {stats['num_temperature_readings']}</td>
							<td>Number of Weather Readings: {stats['num_weather_recordings']}</td>
						</tr>
						<tr>
							<td colspan="2">Average Max Temperature: {stats['avg_max_temperature_reading']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Humidity Reading: {stats['max_humidity_reading']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {getTimeStamp()}</h3>

            </div>
        )
    }
}
