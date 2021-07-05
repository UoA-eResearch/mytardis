import React, { useEffect, useState } from "react";
import { useCreateTransferMutation, useGetObjectByIdQuery, useGetRemoteHostsQuery, useGetSiteQuery, useValidateTransferQuery } from "../shared/api";
import PropTypes from "prop-types";
import { Accordion, Button, Card, Collapse, FormControl } from "react-bootstrap";
import { Link, Redirect, Route, Switch, useRouteMatch } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { getItemsByCategory, removeItem } from "./cartSlice";
import { BsCheck, BsDashCircle, BsExclamationTriangle, BsExclamationTriangleFill, BsFillExclamationCircleFill, BsPlusCircle, BsTrash } from "react-icons/bs";
import { FiExternalLink } from "react-icons/fi";
import { CategoryTabs } from "../shared/CategoryTabs";
import { QueryStatus } from "@reduxjs/toolkit/dist/query";

// eslint-disable-next-line complexity
function CartItemRow({ typeId, id, canTransfer }) {
    const dispatch = useDispatch();
    const { data: site, isLoading: isSiteLoading } = useGetSiteQuery();
    const endpointName = site ? site.categories[typeId].endpoint_name : null;
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
    const nameField = site.categories[typeId].name_field;
    const url = site.categories[typeId].details_uri + id;
    const name = item[nameField];
    return (<tr className={canTransfer ? null : "cart-item--invalid"}>
        <td className="category-item-list--remove">
            {canTransfer ? null : <BsExclamationTriangleFill title="This item can't be transferred because it belongs to a project or dataset that is not associated with the chosen transfer destination." />}
        </td>
        <td className="category-item-list--name">
            {/* Name cell */}
            <a href={url} target="_blank" rel="noopener noreferrer">{name} <FiExternalLink /></a> 
        </td>
        <td className="category-item-list--size">
            <span>{item.size}</span>
        </td>
    </tr>);
}

CartItemRow.propTypes = {
    typeId: PropTypes.string.isRequired,
    id: PropTypes.string.isRequired,
    canTransfer: PropTypes.bool
};



export function CartCategoryTabs({selectedRemoteHost, selectedType, onChange}) {
    const {data: site} = useGetSiteQuery({});
    const { data: validationErrors, isLoading: isValidationLoading, error: validationQueryError } = useValidateTransferQuery({
        remoteHostId: selectedRemoteHost
    });
    const counts = useSelector(state => {
        if (!site) {
            return null;
        }
        const categories = site.categories;
        const categoryKeys = Object.keys(categories);
        return categoryKeys.map(key => {
            const categoryItemsInCart = state.cart.itemsInCart.byId[key] || [];
            return {
                name: site.categories[key].collection_name,
                id: key,
                hitTotal: categoryItemsInCart.length
            };
        });
    });
    if (!counts) {
        return null;
    } else {
        return (<CategoryTabs counts={counts} selectedType={selectedType} onChange={onChange} />);
    }
}

/**
 * Create a React hook for storing the currently selected category. 
 * Get query API, in order to provide a default category.
 * @returns A state variable for a category key, and a callback for changing it.
 */
function useSelectedCategoryState() {
    const [ selectedCategory, setSelectedCategory ] = useState();
    const {data: site, isLoading } = useGetSiteQuery({});

    useEffect(() => {
        // Set default category when our list of categories is loaded.
        // Make sure it's only done when categories loaded.
        if (site) {
            setSelectedCategory(Object.keys(site.categories)[0]);
        }
    }, [setSelectedCategory, site]);
    return [ selectedCategory, setSelectedCategory ];
}

function InvalidItemsWarning({ hostName }) {
    const [open, setOpen] = useState(false);
    // 
    //     <div className="d-flex">
    //         <div style={{fontSize: "2rem"}}>
    //             
    //         </div>
    //         <div className="pl-4">
    //             <h2 className="h5">Some cart items can't be transferred to {remoteHosts[selectedId].name}</h2>

    //         </div>
    //     </div>
    // </div>
    return (
        <>
            <div className="invalid-items-warning mt-2 py-2 px-3"
                role="button"
                aria-live="assertive"
                aria-controls="invalid-items-detail"
                aria-expanded={open}
                onClick={() => setOpen(!open)}>
                <span className="float-right">
                    {open ? <BsDashCircle /> : <BsPlusCircle />}
                </span>

                <span>
                    <BsExclamationTriangle fontSize="1.25rem" /> Some cart items can&apos;t be transferred to {hostName}.
                </span>
            </div>
            <Collapse in={open}>
                <div id="invalid-items-detail" className="border border-top-0 px-3 py-3"> 
                    Some carts can&apos;t be transferred to the destination because they belong to a project or dataset not associated with the chosen destination. You can review the files that are ready for transfer and start a transfer, change your transfer endpoint, or go back to the cart to remove unwanted files.
                </div>
            </Collapse>
        </>
    );
    // <Accordion>
    //     <Card className="mt-3">
    //         <Accordion.Toggle as={Card.Header} className="" eventKey="0">
    //             <BsExclamationTriangle /> Some cart items can&apos;t be transferred to {hostName}
    //         </Accordion.Toggle>
    //         <Accordion.Collapse eventKey="0">
    //             <Card.Body>
    //                 <p>
    //                     This is because they belong to a project or dataset not associated with this destination. You can review the files that are ready for transfer and start a transfer, change your transfer endpoint, or go back to the cart to remove unwanted files.
    //                 </p>
    //             </Card.Body>
    //         </Accordion.Collapse>
    //     </Card>
    // </Accordion>
    //     // <div className="alert alert-primary mt-3" role="alert">
    //     <BsExclamationTriangle /> Some cart items can't be transferred to {remoteHosts[selectedId].name}.
    // </div>
}


// eslint-disable-next-line complexity
function RemoteHostDropdown({selectedId, onSelect}) {
    const { data: remoteHosts, isLoading } = useGetRemoteHostsQuery();
    const { data: validationErrors, isLoading: isValidationLoading, error: validationQueryError } = useValidateTransferQuery({
        remoteHostId: selectedId
    });

    if (isLoading || isValidationLoading) {
        return <p>Loading</p>;
    }
    const selected = selectedId ? remoteHosts[selectedId].name : "";
    const invalidCount = !validationErrors ? 0 : Object.keys(validationErrors.invalidItems)
        .map(categoryId => validationErrors.invalidItems[categoryId].length)
        .reduce((accumulator, value) => accumulator + value, 0);
    let remoteHostOptions, remoteHostIds;
    if (!remoteHosts || Object.keys(remoteHosts).length === 0) {
        remoteHostOptions = <option>No destinations available.</option>;
    } else {
        remoteHostIds = Object.keys(remoteHosts);
        remoteHostOptions = remoteHostIds.map(hostId => 
            <option key={hostId}>
                {remoteHosts[hostId].name}
            </option>);
        // Add a default, unselected option.
        remoteHostOptions.unshift(<option key="notselected">Select a destination</option>);
    }
    const handleSelected = (e) => {
        e.preventDefault();
        const selectedIndex = e.target.selectedIndex;
        if (selectedIndex === 0) {
            onSelect(null);
        } else {
            onSelect(remoteHostIds ? parseInt(remoteHostIds[selectedIndex - 1]) : null);
        }
    };
    return <div className="transfer-screen--remotehost-list">
        <select className="form-control"
            aria-label="Transfer destination"
            size="lg"
            value={selected}
            id="transfer-page--dropdown"
            onChange={handleSelected}
        >
            {remoteHostOptions}
        </select>
        {
            invalidCount > 0 &&
                <InvalidItemsWarning hostName={selected} />
        }
    </div>;
}

RemoteHostDropdown.propTypes = {
    selectedId: PropTypes.string,
    onSelect: PropTypes.func.isRequired
};

function CategoryItemList({ children }) {
    return (<table className="table">
        <thead>
            <tr>
                <th></th>
                <th>Name</th>
                <th>Size</th>
            </tr>
        </thead>
        <tbody>
            {children}
        </tbody>
    </table>);
}

CategoryItemList.propTypes = {
    children: PropTypes.oneOfType([
        PropTypes.arrayOf(PropTypes.node),
        PropTypes.node
    ]).isRequired
};

const VALID_TRANSFER_FILTER_STATES = {
    All: "ALL",
    Invalid: "INVALID",
    Valid: "VALID"
};


function getItemsByState(items = [], invalidItems = [], validState) {
    // const invalidTypeItems = validationErrors.invalidItems ? validationErrors.invalidItems[type] : [];
    // const typeItems = items.byId[typeId];
    switch (validState) {
        case VALID_TRANSFER_FILTER_STATES.All:
            return items;
        case VALID_TRANSFER_FILTER_STATES.Invalid:
            return invalidItems;
        case VALID_TRANSFER_FILTER_STATES.Valid: {
            const invalidSet = new Set(invalidItems);
            return items.filter(item => !invalidSet.has(item));
        }
    }
}


// eslint-disable-next-line complexity
export function TransferrableItemList({selectedRemoteHost}) {
    const {data: site, isLoading, error } = useGetSiteQuery({});
    const [ selectedCategory, setSelectedCategory ] = useSelectedCategoryState();
    const [ validFilterState, setValidFilterState ] = useState(VALID_TRANSFER_FILTER_STATES.All);
    const { data: validationErrors, isLoading: isValidationLoading, error: validationQueryError } = useValidateTransferQuery({
        remoteHostId: selectedRemoteHost
    });
    const items = useSelector(state => state.cart.itemsInCart || {});
    if (isLoading || isValidationLoading) {
        return <p>Loading...</p>;
    }
    if (error || validationQueryError) {
        return <p>Error loading cart.</p>;
    }
    const invalidItems = validationErrors.invalidItems || {};
    const categories = Object.keys(site.categories);
    // Compute which items to display.
    const itemsToDisplay = Object.fromEntries(categories.map(categoryId => 
        [categoryId, getItemsByState(items.byId[categoryId], invalidItems[categoryId], validFilterState)]
    ));
    const tabItems = categories.map(categoryId => 
        ({
            name: site.categories[categoryId].collection_name,
            id: categoryId,
            hitTotal: itemsToDisplay[categoryId].length
        })
    );

    const allCount = Object.keys(items.byId)
        .map(categoryId => items.byId[categoryId].length)
        .reduce((accumulator, value) => accumulator + value, 0);
    const invalidCount = Object.keys(invalidItems)
        .map(categoryId => invalidItems[categoryId].length)
        .reduce((accumulator, value) => accumulator + value, 0);
    const validStateFilterCounts = {
        [VALID_TRANSFER_FILTER_STATES.All]: allCount,
        [VALID_TRANSFER_FILTER_STATES.Invalid]: invalidCount,
        [VALID_TRANSFER_FILTER_STATES.Valid]: allCount - invalidCount
    };

    return (
        <>
            <section className="mt-4">
                <h2 className="h4">Objects to be transferred</h2>
                <p>Review the objects that will be transferred to the destination, then choose Start transfer.</p>
                <CategoryTabs counts={tabItems} selectedType={selectedCategory} onChange={setSelectedCategory} />
                {categories.map(categoryId => {
                    const invalidItemSet = new Set(invalidItems[categoryId]);
                    return <div className={selectedCategory !== categoryId ? "d-none category-item-list" : "category-item-list"} key={categoryId}>
                        <CategoryItemList>
                            {itemsToDisplay[categoryId].map(item => (
                                <CartItemRow typeId={categoryId} id={item} canTransfer={!invalidItemSet.has(item)} key={categoryId + ":" + item} />
                            ))}
                        </CategoryItemList>
                    </div>;
                })}
            </section>
        </>
    );
}
    // if (!validationErrors.invalidItems) {

    // }
    // const hostInfo = hosts[selectedRemoteHost];
    // const cantTransferItems = Object.keys(itemsInCart).map(typeId => {
    //     // Create a set for quicker lookup
    //     const transferrableItems = new Set(hostInfo.transferrableItems[typeId] || []);
    //     return itemsInCart[typeId].filter(itemId => !transferrableItems.has(itemId));
    // });
    // Object.keys(itemsInCart)

const TRANSFER_STATE = {
    Initial: "Initial",
    TransferRequested: "TransferRequested", // set to start a transfer
    NeedConfirmation: "NeedConfirmation", // has invalid items
    Confirmed: "Confirmed", // confirmed
    Transferring: "Transferring", // transferring
    Transferred: "Transferred" // transferred
};

// eslint-disable-next-line complexity
function CreateTransferDialog({remoteHostId, transferState, setTransferState}) {
    const [triggerTransfer, {status: transferMutationStatus}] = useCreateTransferMutation();
    const {data: validation, isLoading} = useValidateTransferQuery({
        remoteHostId
    });
    useEffect(() => {
        if (isLoading || transferState !== TRANSFER_STATE.TransferRequested) {
            // If validation is still being loaded, wait until it's
            // loaded.
            return;
        }
        const invalidItems = validation.invalidItems;
        if (!invalidItems) {
            // If there are no validation errors, we don't need
            // to confirm with the user regarding proceeding with
            // transfer.
            setTransferState(TRANSFER_STATE.Confirmed);
        }
        const numInvalidItems = Object.keys(invalidItems).reduce(
            (acc, categoryId) => invalidItems[categoryId].length + acc, 0);

        if (numInvalidItems > 0) {
            setTransferState(TRANSFER_STATE.NeedConfirmation);
        } else {
            setTransferState(TRANSFER_STATE.Confirmed);
        }
    }, [isLoading, validation, transferState]);

    useEffect(() => {
        if (transferState === TRANSFER_STATE.Confirmed) {
            triggerTransfer({remoteHostId});
            setTransferState(TRANSFER_STATE.Transferring);
        }
    }, [transferState]);
    useEffect(() => {
        if (transferMutationStatus === QueryStatus.fulfilled) {
            setTransferState(TRANSFER_STATE.Transferred);
        }
    }, [transferMutationStatus]);
    if (transferState === TRANSFER_STATE.NeedConfirmation) {
        return (<p>Are you sure you want to send this? 
            <button className="btn" onClick={() => setTransferState(TRANSFER_STATE.Confirmed)}>Yes</button> 
            <button className="btn" onClick={() => setTransferState(TRANSFER_STATE.Initial)}>No</button> 
        </p>);
    }
    if (transferState === TRANSFER_STATE.Confirmed) {
        return <p>Sending...</p>;
    }
    if (transferState === TRANSFER_STATE.Transferred) {
        return <Redirect to="/transfer/done" />;
    }
    else { 
        return null;
    }
}

function TransferScreen(props) {
    const [selectedRemoteHost, setSelectedRemoteHost] = useState();
    const [transferState, setTransferState] = useState(TRANSFER_STATE.Initial);
    return <div>
        <h1 className="h3 my-3">Transfer to an endpoint</h1>
        <p>Select a transfer destination.</p>
        <RemoteHostDropdown selectedId={selectedRemoteHost} onSelect={setSelectedRemoteHost} />
        {selectedRemoteHost ? <TransferrableItemList selectedRemoteHost={selectedRemoteHost} /> : null}
        <div className="d-flex justify-content-between">
            <Link to="/" className="btn btn-secondary">Cancel and go back to cart</Link>
            <button 
                className="btn btn-primary"
                disabled={!selectedRemoteHost}
                aria-disabled={!selectedRemoteHost}
                onClick={() => setTransferState(TRANSFER_STATE.TransferRequested)}
            >
                Start transfer
            </button>
        </div>
        <CreateTransferDialog 
            remoteHostId={selectedRemoteHost} 
            transferState={transferState} 
            setTransferState={setTransferState} 
        />
    </div>;
}

function TransferRoute(props) {
    const match = useRouteMatch();
    return <Switch>
        <Route path={`${match.path}/done`}>
            <p>Transfer finished!</p>
        </Route>
        <Route path={`${match.path}`}>
            <TransferScreen />
        </Route>
    </Switch>;
}

export default TransferRoute;