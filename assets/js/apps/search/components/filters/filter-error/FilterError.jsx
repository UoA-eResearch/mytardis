import React, { useRef, useState } from 'react';
import { FiInfo } from 'react-icons/fi';
import { OverlayTrigger, Tooltip } from 'react-bootstrap';
import './FilterError.css';

const FilterError = ({ message }) => {
    const target = useRef(null);
    return (
        <>
            <OverlayTrigger
                overlay={
                    <Tooltip className='filter-error___tooltip'>{message}</Tooltip>
                }
                delay={{ show: 250, hide: 400 }}
                placement="top"
            >
                <div 
                    ref={target} 
                    aria-label="Filter error message" 
                    className="filter-error"
                >
                    <p>
                        Show Input Error
                    </p>
                    <FiInfo className="filter-error___icon" aria-label="error message icon"></FiInfo>
                </div>
            </OverlayTrigger>
        </>
    )
}
export default FilterError;