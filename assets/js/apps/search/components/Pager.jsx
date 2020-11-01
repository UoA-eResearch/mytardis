import React from 'react';
import PropTypes from "prop-types";
import { 
    Pagination,
    Dropdown
 } from "react-bootstrap";
import { 
    pageSizeSelector,
    pageNumberSelector, 
    totalPagesSelector, 
    updatePageSizeAndRefetch, 
    updatePageNumberAndRefetch 
} from "./searchSlice";
import { useDispatch, useSelector } from "react-redux";
import { useCallback } from 'react';

const nearbyNums = (number, count = 5, min = 1, max) => {
    const nearby = [],
        half = Math.floor(count / 2);
    let firstNumber, howMany;
    if (number - half >= min) {
        if (max - number >= count && half + count <= max) {
            // If the number is towards the middle of the range
            firstNumber = number - half;
            howMany = count;
        } else {
            // If the number is towards end of the range
            firstNumber = max - count + 1;
            howMany = max - firstNumber + 1;
        }
    } else {
        // If the number is towards beginning of the range
        firstNumber = min;
        howMany = Math.min(max, count);
    }
    for (let i = 0; i < howMany; i++) {
        nearby[i] = firstNumber + i;
    }
    return nearby;
};


const renderPageItems = (currentPageNum, maxPages, clickCallback) => {
    const renderedPages = nearbyNums(currentPageNum, 5, 1, maxPages),
        renderedMin = renderedPages[0],
        renderedMax = renderedPages[renderedPages.length - 1];
    let pageItems = [];
    if (renderedMin !== undefined && renderedMin !== 1) {
        pageItems.push(<Pagination.Ellipsis key="ellipsis1" active={false} />);
    }
    pageItems = pageItems.concat(renderedPages.map(
        (number, index) => (
            <Pagination.Item
                onClick={clickCallback.bind(this, number)} 
                active={number === currentPageNum}
                key={index}
            >
                {number}
            </Pagination.Item>
        )
    ));
    if (renderedMax !== undefined &&
        renderedMax !== maxPages) {
        pageItems.push(<Pagination.Ellipsis key="ellipsis2" active={false} />);
        pageItems.push(
            <Pagination.Item 
                key="lastitem"
                active={false} 
                onClick={clickCallback.bind(this, maxPages)}
            >
                {maxPages}
            </Pagination.Item>
        );
    }
    return pageItems;
};

export const PAGE_SIZE_OPTIONS = [20, 50, 200];

const PurePageSizeDropdown = ({typeId, pageSize, onPageSizeChange}) => {
    const handleDropdownSelected = useCallback((e) => {
        e.preventDefault();
        onPageSizeChange(parseInt(e.target.value));
    }, [onPageSizeChange]);
    return (
        <>
        <label htmlFor={typeId + "pagesize-dropdown"}>Items per page</label>
        <select id={typeId + "pagesize-dropdown"} value={pageSize} onChange={handleDropdownSelected}>
            {
                PAGE_SIZE_OPTIONS.map(size => (
                    <option key={size} value={size}>{size}</option>
                ))
            }
        </select>
        </>
        // <Dropdown>
        //     <Dropdown.Toggle id={typeId+"pageSize-dropdown"}>
        //         {pageSize}
        //     </Dropdown.Toggle>
        //     <Dropdown.Menu>
        //         {
        //             PAGE_SIZE_OPTIONS.map(size => (
        //                 <Dropdown.Item key={size} onClick={onPageSizeChange}>{size}</Dropdown.Item>
        //             ))
        //         }
        //     </Dropdown.Menu>
        // </Dropdown>
    );
};

export const PurePager = ({typeId, pageNum, pageSize, totalPages, onPageNumChange, onPageSizeChange}) => {
    const handleClicked = useCallback((newPageNum, event) => {
        event.stopPropagation();
        if (pageNum === newPageNum || newPageNum < 1 || newPageNum > totalPages) {
            return;
        } else {
            onPageNumChange(newPageNum);
        }
    }, [pageNum, totalPages]);
    return (
        <>
            <PurePageSizeDropdown typeId={typeId} pageSize={pageSize} onPageSizeChange={onPageSizeChange} />
            <Pagination>
                <Pagination.First key="first" onClick={handleClicked.bind(this, 1)} />
                <Pagination.Prev key="prev" onClick={handleClicked.bind(this, pageNum - 1)} />
                {renderPageItems(pageNum, totalPages, handleClicked)}
                <Pagination.Next key="next" onClick={handleClicked.bind(this, pageNum + 1)} />
                <Pagination.Last key="last" onClick={handleClicked.bind(this, totalPages)} />
            </Pagination>
        </>
    );
};

PurePager.propTypes = {
    pageNum: PropTypes.number.isRequired,
    pageSize: PropTypes.number.isRequired,
    totalPages: PropTypes.number.isRequired,
    onPageNumChange: PropTypes.func.isRequired,
    onPageSizeChange: PropTypes.func.isRequired
};

/**
 * Redux store-connected Pager component. Use PurePager for testing/storybook purposes.
 */
function Pager({objectType}) {
    const dispatch = useDispatch();
    const pageNum = useSelector(state => (
        pageNumberSelector(state.search, objectType)
    ));
    const pageSize = useSelector(state => (
        pageSizeSelector(state.search, objectType)
    ));
    const totalPages = useSelector(state => (
        totalPagesSelector(state.search, objectType)
    ));
    const handlePageNumChange = useCallback((newPageNum) => {
        dispatch(updatePageNumberAndRefetch(objectType, newPageNum));
    }, [dispatch, objectType]);
    const handlePageSizeChange = useCallback((newPageSize) => {
        dispatch(updatePageSizeAndRefetch(objectType, newPageSize));
    }, [dispatch, objectType]);
    return (
        <PurePager
            typeId={objectType}
            pageNum={pageNum} 
            pageSize={pageSize} 
            totalPages={totalPages} 
            onPageNumChange={handlePageNumChange}
            onPageSizeChange={handlePageSizeChange}
        />
    );
}

Pager.propTypes = {
    objectType: PropTypes.string.isRequired
};

export default Pager;