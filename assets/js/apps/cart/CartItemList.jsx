import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { useDispatch, useSelector } from "react-redux";
import { BsTrash } from "react-icons/bs";
import { FiExternalLink } from "react-icons/fi";
// import Button from "react-bootstrap/Button";
import { TypeTabs } from "../shared/TypeTabs";
import { useGetObjectByIdQuery, useGetSiteQuery } from "../shared/api";
import { getItemsByType, removeItem } from "./cartSlice";
import humanFileSize from "../shared/humanFileSize";

function CartItemRow({ typeId, id }) {
    const dispatch = useDispatch();
    const { data: site, isLoading: isSiteLoading } = useGetSiteQuery();
    const endpointName = site ? site.types[typeId].endpoint_name : null;
    const { isLoading: isObjectLoading, data: item } = useGetObjectByIdQuery({
        name: endpointName,
        id
    }, {
        // Wait for site query to finish loading.
        skip: isSiteLoading
    });
    if (isSiteLoading || isObjectLoading) {
        return <tr></tr>;
    }

    if (!item) {
        return <tr>
            <td rowSpan="3">
                Not found!
            </td>
        </tr>;
    }
    const nameField = site.types[typeId].name_field;
    const url = site.types[typeId].details_uri + id;
    const name = item[nameField];
    const handleRemoveClicked = (e) => {
        e.preventDefault();
        dispatch(removeItem(typeId, id));
    };
    return (<tr>
        <td className="type-item-list--remove">
            <button onClick={handleRemoveClicked} className="btn btn-light"><BsTrash /></button>
        </td>
        <td className="type-item-list--name">
            {/* Name cell */}
            <a href={url} target="_blank" rel="noopener noreferrer">{name} <FiExternalLink /></a> 
        </td>
        <td className="type-item-list--size">
            <span>{humanFileSize(item.size)}</span>
        </td>
    </tr>);
}

CartItemRow.propTypes = {
    typeId: PropTypes.string.isRequired,
    id: PropTypes.string.isRequired
};


function TypeItemList({ typeId }) {
    const typeItems = useSelector(
        state => 
            getItemsByType(state.cart, typeId));

    return (<>
    <table className="table">
        <thead>
            <tr>
                <th></th>
                <th>Name</th>
                <th>Size</th>
            </tr>
        </thead>
        <tbody>
            {typeItems.map(itemId => 
                <CartItemRow typeId={typeId} id={itemId} key={itemId} />
            )}
        </tbody>
    </table>
    {typeItems.length === 0 && 
        <div className="mt-5 d-flex justify-content-center" role="status">
            No items in cart.
        </div>
    }</>);
}

TypeItemList.propTypes = {
    typeId: PropTypes.string.isRequired
};

export function CartTypeTabs({selectedType, onChange}) {
    const {data: site} = useGetSiteQuery({});
    const counts = useSelector(state => {
        if (!site) {
            return null;
        }
        const types = site.types;
        const typeKeys = Object.keys(types);
        return typeKeys.map(key => {
            const typeItemsInCart = state.cart.itemsInCart.byId[key] || [];
            return {
                name: site.types[key].collection_name,
                id: key,
                hitTotal: typeItemsInCart.length
            };
        });
    });
    if (!counts) {
        return null;
    } else {
        return (<TypeTabs counts={counts} selectedType={selectedType} onChange={onChange} />);
    }
}

/**
 * Create a React hook for storing the currently selected type. 
 * Get query API, in order to provide a default type.
 * @returns A state variable for a type key, and a callback for changing it.
 */
function useSelectedTypeState(site) {
    const [ selectedType, setSelectedType ] = useState();

    useEffect(() => {
        // Set default type when our list of types is loaded.
        // Make sure it's only done when types loaded.
        if (site) {
            setSelectedType(Object.keys(site.types)[0]);
        }
    }, [setSelectedType, site]);
    return [ selectedType, setSelectedType ];
}


export default function CartItemList() {
    const {data: site, isLoading } = useGetSiteQuery({});
    const [ selectedType, setSelectedType ] = useSelectedTypeState(site);
    if (isLoading) {
        return <p>Loading...</p>;
    }
    if (!site) {
        return <p>Error loading cart.</p>;
    }
    const types = Object.keys(site.types);

    return (
        <div>
            <CartTypeTabs selectedType={selectedType} onChange={setSelectedType} />
            {types.map(typeId => (
                <div className={selectedType !== typeId ? "d-none type-item-list" : "type-item-list"} key={typeId}>
                    <TypeItemList typeId={typeId} />    
                </div>
            ))}
        </div>
    );
}