import React, { useRef } from 'react';
import { FiInfo } from 'react-icons/fi';
import { OverlayTrigger, Tooltip } from 'react-bootstrap';
import './FilterError.css';

const FilterError = ({ message, longMessage, showIcon }) => {
    const target = useRef(null);
    return (
        <>
            <OverlayTrigger
                overlay={
                    <Tooltip className='filter-error___tooltip'>{longMessage ? longMessage : message}</Tooltip>
                }
                delay={{ show: 250, hide: 400 }}
                placement="bottom"
            >
                <div
                    ref={target}
                    aria-label="Filter error message"
                    className="filter-error"
                >
                    <p className='filter-error___text'>
                        {message}
                    </p>
                    {showIcon ?
                        <FiInfo className="filter-error___icon" aria-label="error message icon"></FiInfo>
                        :
                        null
                    }
                </div>
            </OverlayTrigger>
        </>
    )
}

FilterError.defaultProps = {
    message: 'Invalid input',
    longMessage: null,
    showIcon: false
}

export default FilterError;