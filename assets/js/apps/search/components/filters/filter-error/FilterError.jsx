import React, { useRef, useState } from 'react';
import { FiInfo } from 'react-icons/fi';
import { OverlayTrigger, Tooltip } from 'react-bootstrap';
import './FilterError.css';

const FilterError = ({ message }) => {
    const [show, setShow] = useState(false);
    const target = useRef(null);

    return (
        <>
            <OverlayTrigger
                overlay={
                    <Tooltip>{message}</Tooltip>
                }
                show={show}
                placement="top"
            >
                <div 
                    ref={target} 
                    aria-label="Filter error message" 
                    className="filter-error"
                >
                    <FiInfo className="filter-error___icon" aria-label="error message icon"></FiInfo>
                    <p>
                        Show Input Error
                    </p>
                </div>
            </OverlayTrigger>
        </>
    )
}

export default FilterError;