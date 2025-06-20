import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import Sidebar from './Sidebar';
import Header from './Header';
import { useApp } from '../../contexts/AppContext';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { state } = useApp();

  return (
    <div className="layout-wrapper">
      <Row className="g-0" style={{ minHeight: '100vh' }}>
        {/* Sidebar */}
        <Col 
          md={state.sidebarCollapsed ? 1 : 3} 
          lg={state.sidebarCollapsed ? 1 : 2} 
          className="sidebar-col"
        >
          <Sidebar />
        </Col>

        {/* Main Content */}
        <Col 
          md={state.sidebarCollapsed ? 11 : 9} 
          lg={state.sidebarCollapsed ? 11 : 10} 
          className="main-content-col"
        >
          {/* Header */}
          <Header />
          
          {/* Page Content */}
          <div className="main-content">
            <Container fluid className="px-4 py-3">
              {children}
            </Container>
          </div>
        </Col>
      </Row>
    </div>
  );
};

export default Layout;
