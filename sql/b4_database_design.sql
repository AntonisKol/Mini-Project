-- SECTION B - SQL ENGINEERING
-- b4_database_design.sql
-- Q4. Database Design

-- ============================================================================
-- TABLE 1: SHIPMENT TRACKING TABLE
-- ============================================================================
-- WHY THIS TABLE IS NEEDED:
-- Current system tracks orders but not shipments.
-- Users need to know: When was order shipped? Where is it now? When arrives?
-- This table tracks each shipment's journey from warehouse to customer.
--
-- DESIGN APPROACH:
-- One order can have multiple shipments (split shipments).
-- Each shipment has multiple tracking events (picked, shipped, delivered).
-- Relationships:
-- - shipments.order_id → orders.order_id (many shipments per order)
-- - shipments.shipment_id ← shipment_events.shipment_id (one-to-many)

CREATE TABLE shipments (
    shipment_id INTEGER PRIMARY KEY AUTOINCREMENT,           
    order_id INTEGER NOT NULL,                              
    shipment_date DATE NOT NULL,                             
    carrier_name VARCHAR(100),                               
    tracking_number VARCHAR(100) UNIQUE,                     
    estimated_delivery_date DATE,                           
    actual_delivery_date DATE,                              
    status VARCHAR(50),                                     
    origin_warehouse VARCHAR(100),                          
    destination_address TEXT,                              
    current_location VARCHAR(100),                          
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,         
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,      
    
    FOREIGN KEY (order_id) REFERENCES orders(order_id),     -- Link to orders table
    CHECK (shipment_date <= estimated_delivery_date),       -- Shipment before delivery
    CHECK (status IN ('pending', 'shipped', 'in_transit', 'delivered', 'delayed'))  -- Valid statuses
);

-- INDEXES FOR SHIPMENTS TABLE:
CREATE INDEX idx_shipments_order_id ON shipments(order_id);           -- Find shipments by order
CREATE INDEX idx_shipments_tracking_number ON shipments(tracking_number);  -- Find shipment by tracking
CREATE INDEX idx_shipments_status ON shipments(status);               -- Find shipments by status
CREATE INDEX idx_shipments_delivery_date ON shipments(actual_delivery_date);  -- Find by delivery date

-- ============================================================================
-- TABLE 2: SHIPMENT EVENTS TABLE
-- ============================================================================
-- WHY THIS TABLE IS NEEDED:
-- A shipment has multiple status updates (picked, shipped, in transit, delivered).
-- Each event has a timestamp and location.
-- Users want to see: "Package picked at 2025-01-15 10:30 AM, left warehouse at 2025-01-15 2:00 PM"
--
-- DESIGN APPROACH:
-- One shipment has many events.
-- Relationships:
-- - shipment_events.shipment_id → shipments.shipment_id (many events per shipment)

CREATE TABLE shipment_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,              
    shipment_id INTEGER NOT NULL,                            
    event_type VARCHAR(50) NOT NULL,                        
    event_timestamp DATETIME NOT NULL,                      
    event_location VARCHAR(100),                           
    event_description TEXT,                                 
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id),  -- Link to shipments
    CHECK (event_type IN ('picked', 'shipped', 'in_transit', 'delivered', 'exception', 'returned'))
);

-- INDEXES FOR SHIPMENT EVENTS TABLE:
CREATE INDEX idx_shipment_events_shipment_id ON shipment_events(shipment_id);  -- Find events by shipment
CREATE INDEX idx_shipment_events_timestamp ON shipment_events(event_timestamp);  -- Find events by time

-- ============================================================================
-- TABLE 3: PRODUCT INVENTORY TABLE
-- ============================================================================
-- WHY THIS TABLE IS NEEDED:
-- Current system has products but no inventory tracking.
-- Need to know: How many units in stock? Where stored? Reorder when low?
-- This table tracks inventory levels by location.
--
-- DESIGN APPROACH:
-- One product can be stored in multiple warehouses.
-- Each warehouse tracks quantity on hand, reorder level, etc.
-- Relationships:
-- - inventory.product_id → products.product_id (many inventory rows per product)
-- - inventory.warehouse_id → warehouses.warehouse_id (many inventory rows per warehouse)

CREATE TABLE warehouses (
    warehouse_id INTEGER PRIMARY KEY AUTOINCREMENT,         
    warehouse_name VARCHAR(100) NOT NULL UNIQUE,           
    location_city VARCHAR(50),                             
    location_state VARCHAR(2),                              
    location_country VARCHAR(50),                          
    capacity_units INTEGER,                                
    current_utilization_percent DECIMAL(5,2),             
    manager_name VARCHAR(100),
    contact_phone VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory (
    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,         
    product_id INTEGER NOT NULL,                            
    warehouse_id INTEGER NOT NULL,                          
    quantity_on_hand INTEGER NOT NULL DEFAULT 0,            -- How many units in stock
    quantity_reserved INTEGER DEFAULT 0,                    -- How many reserved for orders
    quantity_available INTEGER GENERATED ALWAYS AS 
        (quantity_on_hand - quantity_reserved) STORED,      -- Available = on hand - reserved
    reorder_level INTEGER,                                  -- Reorder when quantity_on_hand drops below this
    reorder_quantity INTEGER,                               -- Order this many units when reordering
    last_restock_date DATE,                                 -- When last restocked
    last_count_date DATE,                                   -- When last physical count
    unit_cost DECIMAL(10,2),                               
    holding_cost_per_month DECIMAL(10,2),                  -- Monthly storage cost per unit
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (product_id) REFERENCES products(product_id),    -- Link to products
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),  -- Link to warehouses
    UNIQUE (product_id, warehouse_id),                      -- Only one inventory record per product-warehouse combo
    CHECK (quantity_on_hand >= 0),                          -- Can't have negative stock
    CHECK (quantity_reserved >= 0),                         -- Can't have negative reservations
    CHECK (reorder_level > 0)                               -- Reorder point must be positive
);

-- INDEXES FOR INVENTORY TABLE:
CREATE INDEX idx_inventory_product_id ON inventory(product_id);         -- Find inventory by product
CREATE INDEX idx_inventory_warehouse_id ON inventory(warehouse_id);     -- Find inventory by warehouse
CREATE INDEX idx_inventory_quantity_available ON inventory(quantity_available);  -- Find low-stock items
CREATE INDEX idx_inventory_restock_needed ON inventory(quantity_on_hand) 
    WHERE quantity_on_hand <= reorder_level;                -- Find items needing restock

-- ============================================================================
-- TABLE 4: CUSTOMER SUPPORT TICKETS TABLE
-- ============================================================================
-- WHY THIS TABLE IS NEEDED:
-- Current system has customers and orders but no support ticket system.
-- Need to track: What issues reported? How quickly resolved? Who handled it?
-- This table tracks customer support interactions.
--
-- DESIGN APPROACH:
-- One customer can have many support tickets.
-- One ticket can have many messages/responses.
-- One ticket can be related to one order.
-- Relationships:
-- - support_tickets.customer_id → customers.customer_id (many tickets per customer)
-- - support_tickets.order_id → orders.order_id (many tickets per order)
-- - support_tickets.assigned_to_employee_id → employees.employee_id (one employee per ticket)
-- - support_ticket_messages.ticket_id → support_tickets.ticket_id (many messages per ticket)

CREATE TABLE support_tickets (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,            
    customer_id INTEGER NOT NULL,                           
    order_id INTEGER,                                       -- Related order (if applicable)
    ticket_number VARCHAR(20) UNIQUE NOT NULL,             -- Display number (e.g., "TK-2025-00001")
    subject VARCHAR(255) NOT NULL,                          -- "Damaged product", "Wrong item shipped"
    description TEXT NOT NULL,                              -- Full problem description
    category VARCHAR(50),                                   -- 'shipping', 'product_quality', 'order_issue', 'payment', 'other'
    priority VARCHAR(20) DEFAULT 'medium',                  -- 'low', 'medium', 'high', 'urgent'
    status VARCHAR(50) DEFAULT 'open',                      -- 'open', 'in_progress', 'waiting_customer', 'resolved', 'closed'
    assigned_to_employee_id INTEGER,                        -- Which support agent handles it
    assigned_date DATETIME,                                 -- When assigned to agent
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,          -- When ticket created
    first_response_at DATETIME,                             -- When first responded to
    resolved_at DATETIME,                                   -- When resolved
    closed_at DATETIME,                                     -- When closed
    resolution_notes TEXT,                                  -- How was it resolved
    customer_satisfaction_rating INTEGER,                   -- 1-5 stars
    
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),  -- Link to customers
    FOREIGN KEY (order_id) REFERENCES orders(order_id),           -- Link to orders
    CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    CHECK (status IN ('open', 'in_progress', 'waiting_customer', 'resolved', 'closed')),
    CHECK (customer_satisfaction_rating IS NULL OR (customer_satisfaction_rating >= 1 AND customer_satisfaction_rating <= 5))
);

-- INDEXES FOR SUPPORT TICKETS TABLE:
CREATE INDEX idx_support_tickets_customer_id ON support_tickets(customer_id);  -- Find tickets by customer
CREATE INDEX idx_support_tickets_status ON support_tickets(status);            -- Find open tickets
CREATE INDEX idx_support_tickets_priority ON support_tickets(priority);        -- Find urgent tickets
CREATE INDEX idx_support_tickets_assigned_to ON support_tickets(assigned_to_employee_id);  -- Find assigned tickets
CREATE INDEX idx_support_tickets_created_at ON support_tickets(created_at);    -- Find by creation date

-- ============================================================================
-- TABLE 5: SUPPORT TICKET MESSAGES TABLE
-- ============================================================================
-- WHY THIS TABLE IS NEEDED:
-- Tickets need message/comment history.
-- Shows conversation between customer and support agent.
-- Tracks: Who said what, when, and from what channel (email, chat, phone).
--
-- DESIGN APPROACH:
-- One ticket has many messages.
-- Messages from customer OR support agent.
-- Relationships:
-- - support_ticket_messages.ticket_id → support_tickets.ticket_id (many messages per ticket)

CREATE TABLE support_ticket_messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,           -- Unique message ID
    ticket_id INTEGER NOT NULL,                             -- Which ticket
    message_from VARCHAR(20),                               -- 'customer' or 'support_agent'
    from_customer_id INTEGER,                               -- Customer ID (if from customer)
    from_employee_id INTEGER,                               -- Employee ID (if from support agent)
    message_text TEXT NOT NULL,                             -- The actual message
    message_channel VARCHAR(50),                            -- 'email', 'chat', 'phone', 'twitter'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,          -- When message sent
    
    FOREIGN KEY (ticket_id) REFERENCES support_tickets(ticket_id),  -- Link to ticket
    FOREIGN KEY (from_customer_id) REFERENCES customers(customer_id),  -- Link to customer
    CHECK (message_from IN ('customer', 'support_agent'))
);

-- INDEXES FOR SUPPORT TICKET MESSAGES TABLE:
CREATE INDEX idx_support_messages_ticket_id ON support_ticket_messages(ticket_id);  -- Find messages in ticket
CREATE INDEX idx_support_messages_created_at ON support_ticket_messages(created_at);  -- Find by date

-- ============================================================================
-- SUMMARY: DATABASE DESIGN - ALL TABLES CREATED
-- ============================================================================
--
-- TABLE 1: SHIPMENTS & SHIPMENT_EVENTS
--   Purpose: Track order shipments and delivery status
--   Relationships: orders → shipments → shipment_events (1-to-many chain)
--   Key columns: tracking_number, status, estimated_delivery_date
--   Use case: "Where's my order?" tracking
--
-- TABLE 2: WAREHOUSES & INVENTORY
--   Purpose: Track product stock levels by location
--   Relationships: products → inventory ← warehouses (many-to-many through inventory)
--   Key columns: quantity_on_hand, quantity_available, reorder_level
--   Use case: "Do we have this item in stock?"
--
-- TABLE 3: SUPPORT_TICKETS & SUPPORT_TICKET_MESSAGES
--   Purpose: Track customer support issues and resolutions
--   Relationships: customers → support_tickets ← orders (many-to-many)
--                  support_tickets → support_ticket_messages (1-to-many)
--   Key columns: status, priority, assigned_to_employee_id
--   Use case: "What's the status of my support issue?"
--
-- ============================================================================
-- DATABASE DESIGN PRINCIPLES APPLIED
-- ============================================================================
--
-- 1. NORMALIZATION: Each table has single purpose
--    - Shipments table for shipment info (not mixed with orders)
--    - Inventory table for stock (not stored with products)
--    - Support tickets separate from orders
--
-- 2. RELATIONSHIPS: Proper foreign keys prevent data corruption
--    - shipments.order_id references orders.order_id
--    - inventory uses product_id + warehouse_id (composite key)
--    - support_tickets links customer, order, and employee
--
-- 3. CONSTRAINTS: Data validation ensures consistency
--    - CHECK (shipment_date <= estimated_delivery_date)
--    - CHECK (quantity_on_hand >= 0)
--    - CHECK (priority IN ('low', 'medium', 'high', 'urgent'))
--
-- 4. INDEXES: Fast queries on common searches
--    - idx_shipments_status for "find all shipped packages"
--    - idx_inventory_quantity_available for "find low-stock items"
--    - idx_support_tickets_status for "find open tickets"
--
-- 5. COMPUTED COLUMNS: Auto-calculated fields
--    - quantity_available = quantity_on_hand - quantity_reserved
--    - Ensures data consistency (no manual updates needed)
--
-- 6. TIMESTAMPS: Track when records created/updated
--    - created_at: When record first inserted
--    - updated_at: When record last modified
--    - Enables audit trails and change tracking
--
-- ============================================================================