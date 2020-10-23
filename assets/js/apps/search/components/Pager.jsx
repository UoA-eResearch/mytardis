import React from 'react';
import PropTypes from "prop-types";
import { Pagination } from "react-bootstrap";
import { pageSizeSelector, pageNumberSelector, updatePageSize, totalPagesSelector, updatePageNumber } from "./searchSlice";
import { useDispatch, useSelector } from "react-redux";
import { useCallback } from 'react';

const nearbyNums = (number, count = 5, min = 1, max) => {
    const nearby = [],
        half = Math.floor(count / 2);
    let firstNumber;
    if (number - half >= min) {
        if (half + count <= max) {
            firstNumber = number - half;
        } else {
            firstNumber = max - count;
        }
    } else {
        firstNumber = min;
    }
    for (let i = 0; i < count; i++) {
        nearby[i] = firstNumber + i;
    }
    return nearby;
};

const renderPageItems = (currentPageNum, maxPages, clickCallback) => {
    const renderedPages = nearbyNums(currentPageNum, 5, 1, maxPages);
    let pageItems = [];
    if (renderedPages[0] !== 2) {
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
    if (renderedPages[renderedPages.length - 1] !== maxPages - 1) {
        pageItems.push(<Pagination.Ellipsis key="ellipsis2" active={false} />);
    }
    return pageItems;
};

export const PurePager = ({pageNum, pageSize, totalPages, handlePageNumChange}) => {
    const handleClicked = useCallback((number, event) => {
        event.stopPropagation();
        if (pageNum === number) {
            return;
        } else {
            handlePageNumChange(number);
        }
    }, [pageNum]);
    return (
        <Pagination>
            <Pagination.First key="first" onClick={handleClicked.bind(this, 1)} />
            <Pagination.Prev key="prev" onClick={handleClicked.bind(this, pageNum - 1)} />
            {renderPageItems(pageNum, totalPages, handleClicked)}
            <Pagination.Next key="next" onClick={handleClicked.bind(this, pageNum + 1)} />
            <Pagination.Last key="last" onClick={handleClicked.bind(this, totalPages)} />
        </Pagination>
    );
};

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
        dispatch(updatePageNumber({typeId: objectType, number: newPageNum}));
    }, [dispatch, objectType]);
    return (
        <PurePager 
            pageNum={pageNum} 
            pageSize={pageSize} 
            totalPages={totalPages} 
            handlePageNumChange={handlePageNumChange}
        />
    );
}

Pager.propTypes = {
    objectType: PropTypes.string.isRequired
};

export default Pager;