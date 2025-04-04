import React from 'react';
import { LocationDistance } from '../types/property';
import { FaCar, FaBus, FaWalking, FaBuilding, FaShoppingCart, FaSchool, FaTrain, FaBicycle } from 'react-icons/fa';
import { textStyles } from '../styles/textStyles';
import { useTabs } from '../context/TabsContext';

const formatTime = (time?: { text: string; value: number }) => {
    if (!time) return 'N/A';
    return time.text;
};

const LocationRow: React.FC<{ location: LocationDistance }> = ({ location }) => {
    return (
        <tr className={textStyles.table.body.row}>
            <td className={textStyles.table.body.cell}>{location.destination}</td>
            <td className={textStyles.table.body.cell}>{location.distance.text}</td>
            <td className={textStyles.table.body.cell}>
                <div className="flex items-center space-x-2">
                    {location.modes.driving?.current && (
                        <div className="flex items-center space-x-1">
                            <FaCar className={textStyles.icon.regular} />
                            <span className={textStyles.body.regular}>{formatTime(location.modes.driving.current)}</span>
                        </div>
                    )}
                </div>
            </td>
            <td className={textStyles.table.body.cell}>
                <div className="flex items-center space-x-2">
                    {location.modes.transit?.current && (
                        <div className="flex items-center space-x-1">
                            <FaBus className={textStyles.icon.regular} />
                            <span className={textStyles.body.regular}>{formatTime(location.modes.transit.current)}</span>
                        </div>
                    )}
                </div>
            </td>
            <td className={textStyles.table.body.cell}>
                <div className="flex items-center space-x-2">
                    {location.modes.walking?.current && (
                        <div className="flex items-center space-x-1">
                            <FaWalking className={textStyles.icon.regular} />
                            <span className={textStyles.body.regular}>{formatTime(location.modes.walking.current)}</span>
                        </div>
                    )}
                </div>
            </td>
        </tr>
    );
};

export default function DistanceInfoDisplay() {
    const { distanceInfo } = useTabs();

    if (!distanceInfo) return null;

    return (
        <div className={textStyles.layout.container}>
            {distanceInfo.work && distanceInfo.work.length > 0 && (
                <div>
                    <div className={textStyles.section.container}>
                        <FaBuilding className={textStyles.icon.colored.work} />
                        <h2 className={textStyles.section.header}>Work Locations</h2>
                    </div>
                    <div className={textStyles.table.container}>
                        <table className={textStyles.table.wrapper}>
                            <thead>
                                <tr className={textStyles.table.header.row}>
                                    <th className={textStyles.table.header.cell}>Location</th>
                                    <th className={textStyles.table.header.cell}>Distance</th>
                                    <th className={textStyles.table.header.cell}>Driving</th>
                                    <th className={textStyles.table.header.cell}>Public Transport</th>
                                    <th className={textStyles.table.header.cell}>Walking</th>
                                </tr>
                            </thead>
                            <tbody>
                                {distanceInfo.work.map((location, index) => (
                                    <LocationRow key={index} location={location} />
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
            
            {distanceInfo.groceries && distanceInfo.groceries.length > 0 && (
                <div>
                    <div className={textStyles.section.container}>
                        <FaShoppingCart className={textStyles.icon.colored.groceries} />
                        <h2 className={textStyles.section.header}>Grocery Stores</h2>
                    </div>
                    <div className={textStyles.table.container}>
                        <table className={textStyles.table.wrapper}>
                            <thead>
                                <tr className={textStyles.table.header.row}>
                                    <th className={textStyles.table.header.cell}>Store</th>
                                    <th className={textStyles.table.header.cell}>Distance</th>
                                    <th className={textStyles.table.header.cell}>Driving</th>
                                    <th className={textStyles.table.header.cell}>Public Transport</th>
                                    <th className={textStyles.table.header.cell}>Walking</th>
                                </tr>
                            </thead>
                            <tbody>
                                {distanceInfo.groceries.map((location, index) => (
                                    <LocationRow key={index} location={location} />
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
            
            {distanceInfo.schools && distanceInfo.schools.length > 0 && (
                <div>
                    <div className={textStyles.section.container}>
                        <FaSchool className={textStyles.icon.colored.schools} />
                        <h2 className={textStyles.section.header}>Schools</h2>
                    </div>
                    <div className={textStyles.table.container}>
                        <table className={textStyles.table.wrapper}>
                            <thead>
                                <tr className={textStyles.table.header.row}>
                                    <th className={textStyles.table.header.cell}>School</th>
                                    <th className={textStyles.table.header.cell}>Distance</th>
                                    <th className={textStyles.table.header.cell}>Driving</th>
                                    <th className={textStyles.table.header.cell}>Public Transport</th>
                                    <th className={textStyles.table.header.cell}>Walking</th>
                                </tr>
                            </thead>
                            <tbody>
                                {distanceInfo.schools.map((location, index) => (
                                    <LocationRow key={index} location={location} />
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
} 